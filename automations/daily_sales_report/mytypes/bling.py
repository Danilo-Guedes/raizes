from typing import TypedDict

Access_Data = TypedDict(
    "Access_Data",
    {
        "access_token": str,
        "expires_in": int,
        "token_type": str,
        "scope": str,
        "refresh_token": str,
    },
    total=True,
)