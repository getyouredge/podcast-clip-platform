# main.py (HEALTHCHECK FIX)
# ========================
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
from pathlib import Path

app = FastAPI(title="ClipVote Platform")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data (in-memory for now)
clips_data = [
    {
        "id": "1",
        "title": "Remote Work is Making Us Stupid",
        "description": "Tech CEO claims remote work is destroying creativity and innovation",
        "start_time_seconds": 1456.2,
        "end_time_seconds": 1523.8,
        "transcript_text": "I'm going to say something controversial: remote work is making us collectively dumber. When you're not in the same room, you lose all the magic of spontaneous collaboration.",
        "tags": ["remote-work", "productivity", "controversy"],
        "best_votes": 347,
        "worst_votes": 892,
        "vote_score": -545,
        "controversy_score": 0.72,
        "is_featured": True,
        "created_at": "2025-05-25T10:30:00Z",
        "episode_title": "The Future of Work",
        "podcast_name": "Tech Leaders Daily"
    },
    {
        "id": "2",
        "title": "Bitcoin Will Replace the Dollar by 2030",
        "description": "Former Goldman Sachs exec predicts complete collapse of traditional banking",
        "start_time_seconds": 2890.5,
        "end_time_seconds": 2945.3,
        "transcript_text": "Mark my words: by 2030, Bitcoin will be the global reserve currency. The Fed has printed us into oblivion, and smart money knows it.",
        "tags": ["bitcoin", "crypto", "prediction"],
        "best_votes": 1243,
        "worst_votes": 567,
        "vote_score": 676,
        "controversy_score": 0.31,
        "is_featured": True,
        "created_at": "2025-05-24T14:15:00Z",
        "episode_title": "Crypto Revolution",
        "podcast_name": "Financial Underground"
    },
    {
        "id": "3",
        "title": "Social Media Should be Age-Restricted Like Alcohol",
        "description": "Neuroscientist argues that social platforms are more addictive than gambling",
        "start_time_seconds": 892.1,
        "end_time_seconds": 967.4,
        "transcript_text": "We regulate alcohol, tobacco, gambling - but we give unlimited social media access to 8-year-olds. The dopamine manipulation is more sophisticated than any casino.",
        "tags": ["social-media", "neuroscience", "regulation"],
        "best_votes": 2156,
        "worst_votes": 234,
        "vote_score": 1922,
        "controversy_score": 0.10,
        "is_featured": True,
        "created_at": "2025-05-23T16:45:00Z",
        "episode_title": "Digital Addiction Crisis",
        "podcast_name": "Brain Science Today"
    }
]

class VoteRequest(BaseModel):
    vote_type: str

# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Serve the main frontend page"""
    try:
        # Check if static/index.html exists
        if Path("static/index.html").exists():
            return FileResponse("static/index.html")
        elif Path("index.html").exists():
            return FileResponse("index.html")
        else:
            # Return a simple HTML if no file found
            return HTMLResponse("""
            <!DOCTYPE html>
            <html><head><title>ClipVote</title></head>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>🎧 ClipVote Platform</h1>
                <p>Backend is running successfully!</p>
                <p><a href="/api/clips">View API: /api/clips</a></p>
                <p><a href="/api/stats">View Stats: /api/stats</a></p>
            </body></html>
            """)
    except Exception as e:
        return HTMLResponse(f"<h1>ClipVote Backend Running</h1><p>Error: {str(e)}</p>")

# Health check endpoint (this is what Railway is testing)
@app.get("/api/stats")
async def get_stats():
    """Health check and stats endpoint"""
    try:
        total_votes = sum(clip["best_votes"] + clip["worst_votes"] for clip in clips_data)
        
        return {
            "status": "healthy",
            "total_clips": len(clips_data),
            "total_votes": total_votes,
            "active_users": 892,
            "trending_clips": len([c for c in clips_data if c["is_featured"]])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/clips")
async def get_clips(sort_by: str = Query("vote_score")):
    """Get all clips with sorting"""
    try:
        clips = clips_data.copy()
        
        if sort_by == "vote_score":
            clips.sort(key=lambda x: x["vote_score"], reverse=True)
        elif sort_by == "created_at":
            clips.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "controversy_score":
            clips.sort(key=lambda x: x["controversy_score"], reverse=True)
        
        return clips
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/clips/{clip_id}/vote")
async def vote_on_clip(clip_id: str, vote_data: VoteRequest):
    """Vote on a clip"""
    try:
        for clip in clips_data:
            if clip["id"] == clip_id:
                if vote_data.vote_type == "best":
                    clip["best_votes"] += 1
                elif vote_data.vote_type == "worst":
                    clip["worst_votes"] += 1
                
                # Recalculate scores
                clip["vote_score"] = clip["best_votes"] - clip["worst_votes"]
                total_votes = clip["best_votes"] + clip["worst_votes"]
                if total_votes > 0:
                    clip["controversy_score"] = min(clip["best_votes"], clip["worst_votes"]) / total_votes
                
                return {"status": "success", "message": "Vote recorded"}
        
        return {"status": "error", "message": "Clip not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Additional health check routes
@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "ok", "message": "ClipVote backend is running"}

@app.get("/ping")
async def ping():
    """Ping endpoint"""
    return {"ping": "pong"}

# Main app runner
if __name__ == "__main__":
    import uvicorn
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
