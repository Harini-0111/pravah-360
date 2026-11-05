"""
NASA Earthdata Authentication and Data Access Service.
Provides secure credential management, URS redirect handling,
Earthdata Login token generation, and resilient data streaming.

Adheres strictly to NASA Earthdata Login (EDL / URS v4) and Earthdata Cloud standards.
"""
import os
import time
import requests
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

EDL_URS_HOST = "urs.earthdata.nasa.gov"
EDL_TOKEN_VERIFY_URL = f"https://{EDL_URS_HOST}/api/users/tokens"
EDL_TOKEN_CREATE_URL = f"https://{EDL_URS_HOST}/api/users/find_or_create_token"

class EarthdataRedirectSession(requests.Session):
    """
    Custom requests.Session that preserves HTTP Basic Authentication
    when redirected from a NASA DAAC host to the Earthdata Login URS authority.
    """
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if "Authorization" in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != EDL_URS_HOST:
                del headers["Authorization"]
        return

class NASAAuthService:
    def __init__(self, env_path: Optional[str] = None):
        if env_path and os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            load_dotenv()
            
        self._username = os.getenv("NASA_EARTHDATA_USERNAME", "").strip()
        self._password = os.getenv("NASA_EARTHDATA_PASSWORD", "").strip()
        self._is_configured = bool(
            self._username and 
            self._password and 
            self._username != "your-earthdata-username" and
            self._password != "your-earthdata-password"
        )
        self._bearer_token = None

    @property
    def is_configured(self) -> bool:
        return self._is_configured

    @property
    def username_masked(self) -> str:
        if not self._username:
            return "UNCONFIGURED"
        if len(self._username) <= 4:
            return self._username[0] + "***"
        return self._username[:3] + "***" + self._username[-1]

    def get_session(self) -> requests.Session:
        """
        Creates an authenticated session configured for NASA EDL redirects.
        """
        session = EarthdataRedirectSession()
        if self._is_configured:
            session.auth = (self._username, self._password)
        session.headers.update({
            "User-Agent": "FloodIntelligenceSystem-NASAClient/1.0"
        })
        return session

    def test_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Performs a single, non-destructive authentication verification request
        against NASA Earthdata's official token endpoint.
        """
        if not self._is_configured:
            return False, "CREDENTIALS_MISSING", {
                "error": "NASA_EARTHDATA_USERNAME or NASA_EARTHDATA_PASSWORD not configured in .env",
                "username_configured": bool(self._username),
                "password_configured": bool(self._password)
            }

        headers = {"Accept": "application/json"}
        try:
            resp = requests.get(
                EDL_TOKEN_VERIFY_URL,
                auth=(self._username, self._password),
                headers=headers,
                timeout=20
            )
            
            if resp.status_code == 200:
                return True, "AUTHENTICATION_SUCCESSFUL", {
                    "status_code": 200,
                    "endpoint": EDL_TOKEN_VERIFY_URL,
                    "message": "Credentials verified successfully against Earthdata Login."
                }
            elif resp.status_code == 401:
                try:
                    err_json = resp.json()
                    err_type = err_json.get("error", "unauthorized")
                    err_desc = err_json.get("error_description", "Invalid user credentials")
                except Exception:
                    err_type = "unauthorized"
                    err_desc = resp.text.strip()
                    
                return False, "INVALID_CREDENTIALS", {
                    "status_code": 401,
                    "error_type": err_type,
                    "error_description": err_desc,
                    "explanation": "The username or password provided was rejected by urs.earthdata.nasa.gov."
                }
            elif resp.status_code == 403:
                return False, "EULA_OR_ACTIVATION_REQUIRED", {
                    "status_code": 403,
                    "error_description": resp.text.strip(),
                    "explanation": "Account may require email verification or acceptance of terms."
                }
            else:
                return False, "UNEXPECTED_STATUS", {
                    "status_code": resp.status_code,
                    "response": resp.text[:300]
                }
        except requests.exceptions.Timeout:
            return False, "NETWORK_TIMEOUT", {"error": "Connection timed out connecting to urs.earthdata.nasa.gov"}
        except requests.exceptions.ConnectionError as ce:
            return False, "NETWORK_CONNECTION_ERROR", {"error": str(ce)}
        except Exception as e:
            return False, "CLIENT_ERROR", {"error": str(e)}

    def get_bearer_token(self) -> Optional[str]:
        """
        Retrieves or generates an Earthdata Login Bearer token for Earthdata Cloud access.
        """
        if self._bearer_token:
            return self._bearer_token
            
        session = self.get_session()
        try:
            resp = session.post(EDL_TOKEN_CREATE_URL, timeout=20)
            if resp.status_code == 200:
                self._bearer_token = resp.json().get("access_token")
                return self._bearer_token
            else:
                return None
        except Exception:
            return None

    def download_file(
        self,
        url: str,
        dest_path: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Downloads a file from NASA Earthdata Cloud / DAAC endpoints using Bearer token or Basic auth.
        Handles EULA resolution detection and prevents infinite 401/403 retry loops.
        """
        if not self._is_configured:
            return False, "Credentials not configured in .env", {}

        token = self.get_bearer_token()
        headers = {
            "User-Agent": "FloodIntelligenceSystem-NASAClient/1.0"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        
        for attempt in range(1, max_retries + 1):
            try:
                # If using Bearer token, make direct request
                resp = requests.get(url, headers=headers, stream=True, timeout=60)
                
                # Check for EULA failure or access denied JSON response
                if resp.status_code == 403:
                    try:
                        err_json = resp.json()
                        desc = err_json.get("error_description", "")
                        res_url = err_json.get("resolution_url", "")
                        if "EULA" in desc or "approve" in res_url:
                            return False, "EULA_ACCEPTANCE_REQUIRED", {
                                "status_code": 403,
                                "error": desc,
                                "resolution_url": res_url
                            }
                    except Exception:
                        pass
                    return False, f"HTTP 403 Forbidden: {resp.text[:200]}", {"status_code": 403}

                elif resp.status_code == 401:
                    return False, "HTTP 401 Unauthorized: Authorization not accepted.", {"status_code": 401}

                elif resp.status_code == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "html" in content_type.lower():
                        return False, "Received HTML instead of binary data. Authentication/redirect failed.", {"status_code": 200}
                        
                    temp_dest = dest_path + ".part"
                    with open(temp_dest, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    os.rename(temp_dest, dest_path)
                    return True, "DOWNLOAD_SUCCESS", {
                        "status_code": 200,
                        "file_size": os.path.getsize(dest_path),
                        "file_path": dest_path
                    }

                elif resp.status_code in (500, 502, 503, 504):
                    if attempt < max_retries:
                        time.sleep(backoff_factor ** attempt)
                        continue
                    return False, f"Server error: HTTP {resp.status_code}", {"status_code": resp.status_code}
                else:
                    return False, f"Download failed with HTTP {resp.status_code}", {"status_code": resp.status_code}

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as net_err:
                if attempt < max_retries:
                    time.sleep(backoff_factor ** attempt)
                    continue
                return False, f"Network error after {max_retries} attempts: {net_err}", {}
            except Exception as ex:
                return False, f"Unexpected download exception: {ex}", {}
                
        return False, "Max retries exceeded", {}
