from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field, EmailStr, constr
from typing import List, Optional
from enum import Enum
import uvicorn

app = FastAPI(
    title="CMS & Social API",
    description="A sample API for testing String Constraints, Enums, and Security intents.",
    version="1.0.0"
)

# --- 1. STRING CONSTRAINTS & FORMATS (User Profile) ---

class UserProfile(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Alphanumeric username with underscores."
    )
    email: EmailStr = Field(..., description="Valid email address")
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500, description="Short bio")
    website: Optional[str] = Field(None, pattern=r"^https?://", description="Website URL starting with http/https")

@app.post("/users/profile", status_code=201, tags=["User Profiles"])
async def create_user_profile(profile: UserProfile):
    """
    Creates a user profile. 
    Tests: 
    - BOUNDARY_MIN/MAX_LENGTH (username, bio)
    - PATTERN_MISMATCH (username, website)
    - FORMAT_INVALID (email)
    - REQUIRED_FIELD_MISSING (username, email, full_name)
    """
    return {"message": "Profile created", "username": profile.username}


# --- 2. ENUMS & ARRAYS (Posts) ---

class PostStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class BlogPost(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    status: PostStatus = Field(..., description="Post publication status")
    tags: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=10, 
        description="List of tags"
    )
    category: Optional[str] = Field(None, description="Category (optional)")

@app.post("/posts/create", status_code=201, tags=["Posts"])
async def create_post(post: BlogPost):
    """
    Creates a blog post.
    Tests:
    - ENUM_MISMATCH (status)
    - BOUNDARY_MIN/MAX_ITEMS (tags)
    - TYPE_VIOLATION (tags must be array)
    """
    return {"message": "Post created", "id": 123, "status": post.status}


# --- 3. SECURITY & INJECTIONS (Comments & Search) ---

class Comment(BaseModel):
    post_id: int
    user_id: int
    text: str = Field(..., description="Comment text. Vulnerable to XSS/SQLi if not sanitized.")

@app.post("/comments/add", status_code=201, tags=["Comments"])
async def add_comment(comment: Comment):
    """
    Adds a comment.
    Tests:
    - XSS_INJECTION (text)
    - SQL_INJECTION (text)
    - WHITESPACE_ONLY (text)
    """
    # Simulate processing
    return {"message": "Comment added"}

@app.get("/posts/search", tags=["Search"])
async def search_posts(
    q: str = Query(..., description="Search query string"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Search endpoint.
    Tests:
    - SQL_INJECTION (q)
    - TYPE_VIOLATION (limit)
    - BOUNDARY_MIN/MAX (limit)
    """
    return {"results": [], "query": q}

@app.get("/users/{username}", tags=["User Profiles"])
async def get_user(
    username: str = Path(..., description="Username to fetch")
):
    """
    Get user by username.
    Tests:
    - SQL_INJECTION (username - path param)
    - RESOURCE_NOT_FOUND (if we mock 404)
    """
    return {"username": username, "id": 1}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
