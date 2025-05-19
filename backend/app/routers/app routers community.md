# app/routers/community_router.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.community_model import PostCreate, CommentCreate
from app.auth.auth_utils import get_current_user

router = APIRouter(tags=["Community"])

@router.post("/posts")
async def create_post(post: PostCreate, user=Depends(get_current_user)):
    post_data = {
        "title": post.title,
        "content": post.content,
        "author_id": user["id"],
        "author_role": user["role"],
        "created_at": datetime.utcnow(),
        "comments": []
    }
    # Insert into MongoDB collection
    result = await posts_collection.insert_one(post_data)
    return {"message": "Post created successfully"}

@router.get("/posts")
async def get_posts():
    posts = await posts_collection.find().sort("created_at", -1).to_list(100)
    return posts

@router.post("/comments/{post_id}")
async def add_comment(post_id: str, comment: CommentCreate, user=Depends(get_current_user)):
    comment_data = {
        "content": comment.content,
        "author_id": user["id"],
        "author_role": user["role"],
        "created_at": datetime.utcnow()
    }
    # Update post with new comment
    await posts_collection.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment_data}}
    )
    return {"message": "Comment added successfully"}
