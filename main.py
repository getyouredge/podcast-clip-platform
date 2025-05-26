
# ========================
# main.py (Simplified Backend)
# ========================
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, ARRAY, func, select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import os
from pathlib import Path

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/podcast_clips")
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Simple database models
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(100))
    reputation_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(500), nullable=False)
    podcast_name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_seconds = Column(Integer)
    published_at = Column(DateTime)
    thumbnail_url = Column(Text)
    external_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Clip(Base):
    __tablename__ = "clips"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"))
    title = Column(String(300), nullable=False)
    description = Column(Text)
    start_time_seconds = Column(Float, nullable=False)
    end_time_seconds = Column(Float, nullable=False)
    transcript_text = Column(Text)
    tags = Column(ARRAY(String), default=[])
    best_votes = Column(Integer, default=0)
    worst_votes = Column(Integer, default=0)
    vote_score = Column(Integer, default=0)
    controversy_score = Column(Float, default=0.0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClipVote(Base):
    __tablename__ = "clip_votes"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    clip_id = Column(String, ForeignKey("clips.id"))
    user_id = Column(String, ForeignKey("users.id"))
    vote_type = Column(String(10), nullable=False)  # 'best' or 'worst'
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class ClipResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    start_time_seconds: float
    end_time_seconds: float
    transcript_text: Optional[str]
    tags: List[str]
    best_votes: int
    worst_votes: int
    vote_score: int
    controversy_score: float
    is_featured: bool
    created_at: datetime
    episode_title: str
    podcast_name: str

class VoteCreate(BaseModel):
    vote_type: str

app = FastAPI(title="Podcast Clip Platform")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Create tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Add sample data if empty
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(Clip.id)))
        if result.scalar() == 0:
            await add_sample_data(session)

async def add_sample_data(session: AsyncSession):
    """Add sample clips for demo"""
    
    # Sample episode
    episode = Episode(
        id="ep1",
        title="The Future of Work with Sarah Chen",
        podcast_name="Tech Talk Daily",
        description="Discussion about remote work trends",
        duration_seconds=3600,
        published_at=datetime.now() - timedelta(days=2),
        thumbnail_url="https://images.unsplash.com/photo-1494790108755-2616b332c7-c/150x150",
        external_url="https://example.com/episode"
    )
    session.add(episode)
    
    # Sample clips
    clips = [
        Clip(
            id="clip1",
            episode_id="ep1",
            title="Remote Work is Fundamentally Broken",
            description="A controversial take on why remote work culture is failing companies",
            start_time_seconds=120.5,
            end_time_seconds=165.8,
            transcript_text="The problem with remote work is that we're trying to replicate office culture instead of creating something new. We're just digitizing bad habits and wondering why productivity is down.",
            tags=["remote-work", "productivity", "culture"],
            best_votes=156,
            worst_votes=23,
            vote_score=133,
            controversy_score=0.15,
            is_featured=True
        ),
        Clip(
            id="clip2",
            episode_id="ep1",
            title="Why Bitcoin Will Hit $1M by 2030",
            description="Bold prediction with surprising reasoning about cryptocurrency",
            start_time_seconds=890.2,
            end_time_seconds=928.7,
            transcript_text="Everyone talks about adoption and scarcity, but they're missing the real driver. It's not about technology - it's about geopolitics. When central banks start failing, Bitcoin becomes the only stable store of value.",
            tags=["bitcoin", "crypto", "prediction"],
            best_votes=89,
            worst_votes=67,
            vote_score=22,
            controversy_score=0.43,
            is_featured=False
        ),
        Clip(
            id="clip3",
            episode_id="ep1",
            title="Social Media is Digital Cocaine",
            description="Neuroscientist explains social media addiction",
            start_time_seconds=1456.1,
            end_time_seconds=1518.4,
            transcript_text="The dopamine hits from likes and comments trigger the exact same neural pathways as substance addiction. We've created digital cocaine and given it to our children.",
            tags=["neuroscience", "social-media", "addiction"],
            best_votes=234,
            worst_votes=12,
            vote_score=222,
            controversy_score=0.05,
            is_featured=True
        )
    ]
    
    for clip in clips:
        session.add(clip)
    
    await session.commit()

# API Routes
@app.get("/")
async def root():
    return {"message": "Podcast Clip Platform API"}

@app.get("/api/clips", response_model=List[ClipResponse])
async def get_clips(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("vote_score"),
    db: AsyncSession = Depends(get_db)
):
    """Get clips with sorting"""
    
    query = select(Clip, Episode.title.label('episode_title'), Episode.podcast_name).join(Episode)
    
    if sort_by == "vote_score":
        query = query.order_by(desc(Clip.vote_score))
    elif sort_by == "created_at":
        query = query.order_by(desc(Clip.created_at))
    elif sort_by == "controversy_score":
        query = query.order_by(desc(Clip.controversy_score))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    return [
        ClipResponse(
            id=row.Clip.id,
            title=row.Clip.title,
            description=row.Clip.description,
            start_time_seconds=row.Clip.start_time_seconds,
            end_time_seconds=row.Clip.end_time_seconds,
            transcript_text=row.Clip.transcript_text,
            tags=row.Clip.tags or [],
            best_votes=row.Clip.best_votes,
            worst_votes=row.Clip.worst_votes,
            vote_score=row.Clip.vote_score,
            controversy_score=row.Clip.controversy_score,
            is_featured=row.Clip.is_featured,
            created_at=row.Clip.created_at,
            episode_title=row.episode_title,
            podcast_name=row.podcast_name
        )
        for row in rows
    ]

@app.post("/api/clips/{clip_id}/vote")
async def vote_on_clip(clip_id: str, vote_data: VoteCreate, db: AsyncSession = Depends(get_db)):
    """Vote on a clip (simplified - no user auth for demo)"""
    
    # Get clip
    result = await db.execute(select(Clip).where(Clip.id == clip_id))
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    # Update vote counts (simplified)
    if vote_data.vote_type == "best":
        clip.best_votes += 1
    elif vote_data.vote_type == "worst":
        clip.worst_votes += 1
    
    clip.vote_score = clip.best_votes - clip.worst_votes
    clip.controversy_score = min(clip.best_votes, clip.worst_votes) / max(clip.best_votes + clip.worst_votes, 1)
    
    await db.commit()
    return {"status": "success"}

@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get platform statistics"""
    
    total_clips_result = await db.execute(select(func.count(Clip.id)))
    total_clips = total_clips_result.scalar()
    
    total_votes_result = await db.execute(select(func.sum(Clip.best_votes + Clip.worst_votes)))
    total_votes = total_votes_result.scalar() or 0
    
    return {
        "total_clips": total_clips,
        "total_votes": total_votes,
        "active_users": 892,  # Placeholder
        "trending_clips": 24   # Placeholder
    }

# Serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend for all non-API routes"""
    if path.startswith("api/"):
        raise HTTPException(status_code=404)
    
    file_path = Path("static") / (path or "index.html")
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
