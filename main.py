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

clips_data = [
    {
        "id": "dt1",
        "title": "AI Will Make Human Soldiers Obsolete by 2035",
        "description": "Former DARPA director predicts autonomous weapons will replace infantry",
        "start_time_seconds": 1456.2,
        "end_time_seconds": 1523.8,
        "transcript_text": "We're kidding ourselves if we think humans will be on future battlefields. AI doesn't get scared, doesn't make emotional decisions, and can process information 1000x faster. By 2035, sending human soldiers into combat will be considered barbaric. The military that embraces full autonomy first wins the next war.",
        "tags": ["ai-warfare", "autonomous-weapons", "future-military", "controversial"],
        "best_votes": 287,
        "worst_votes": 1456,
        "vote_score": -1169,
        "controversy_score": 0.84,
        "is_featured": True,
        "created_at": "2025-05-25T10:30:00Z",
        "episode_title": "The Autonomous Battlefield",
        "podcast_name": "Defense Tech Underground"
    },
    {
        "id": "dt2", 
        "title": "Ukraine Proved the Pentagon Fights the Last War",
        "description": "War on the Rocks analyst tears apart US military procurement priorities",
        "start_time_seconds": 2145.3,
        "end_time_seconds": 2198.7,
        "transcript_text": "Ukraine exposed that we've been preparing for the wrong war for 20 years. We spent trillions on fighter jets while Ukraine is winning with $500 drones. The Pentagon is stuck in 1991, buying exquisite systems for wars that will never happen. Meanwhile, China is mass-producing cheap, disposable weapons that actually matter.",
        "tags": ["ukraine-war", "pentagon", "procurement", "drones"],
        "best_votes": 2134,
        "worst_votes": 445,
        "vote_score": 1689,
        "controversy_score": 0.17,
        "is_featured": True,
        "created_at": "2025-05-24T14:15:00Z",
        "episode_title": "Lessons from Ukraine",
        "podcast_name": "War on the Rocks Podcast"
    },
    {
        "id": "dt3",
        "title": "We're Already in World War III with China",
        "description": "NSC advisor argues the cyber and economic war has already begun",
        "start_time_seconds": 892.1,
        "end_time_seconds": 967.4,
        "transcript_text": "Stop talking about preventing World War III with China - we're already in it. They're stealing our intellectual property, infiltrating our defense contractors, and conducting cyber operations against our infrastructure daily. The only question is when the shooting starts. We need to stop pretending this is competition and start treating it like war.",
        "tags": ["china", "cyber-warfare", "ww3", "geopolitics"],
        "best_votes": 1876,
        "worst_votes": 892,
        "vote_score": 984,
        "controversy_score": 0.32,
        "is_featured": True,
        "created_at": "2025-05-23T16:45:00Z",
        "episode_title": "The New Cold War",
        "podcast_name": "Shield of the Republic"
    },
    {
        "id": "dt4",
        "title": "Defense Contractors Are Scamming Taxpayers",
        "description": "Pentagon insider exposes cost overruns and deliberate delays",
        "start_time_seconds": 1678.5,
        "end_time_seconds": 1734.2,
        "transcript_text": "Lockheed, Boeing, Raytheon - they're not defense companies, they're welfare queens. The F-35 program is 15 years late and $200 billion over budget by design. They have no incentive to deliver on time or on budget. Congress keeps writing checks, and contractors keep missing deadlines. It's legalized theft.",
        "tags": ["defense-contractors", "f35", "pentagon-waste", "corruption"],
        "best_votes": 3245,
        "worst_votes": 234,
        "vote_score": 3011,
        "controversy_score": 0.07,
        "is_featured": True,
        "created_at": "2025-05-22T11:20:00Z",
        "episode_title": "Pentagon Procurement Problems",
        "podcast_name": "Defense One Radio"
    },
    {
        "id": "dt5",
        "title": "Nuclear Weapons Are Useless in Modern War",
        "description": "Strategist argues nukes are Cold War relics with no battlefield utility",
        "start_time_seconds": 567.8,
        "end_time_seconds": 623.2,
        "transcript_text": "Nuclear weapons are the most expensive paperweights in history. You can't use them against terrorists, cyber attacks, or hybrid warfare. China is conquering territories with fishing boats and Ukraine is winning with drones. Meanwhile, we're spending $2 trillion on weapons we'll never use. It's strategic malpractice.",
        "tags": ["nuclear-weapons", "strategy", "defense-spending", "cold-war"],
        "best_votes": 567,
        "worst_votes": 1789,
        "vote_score": -1222,
        "controversy_score": 0.76,
        "is_featured": False,
        "created_at": "2025-05-21T09:15:00Z",
        "episode_title": "Rethinking Nuclear Strategy",
        "podcast_name": "Lawfare Podcast"
    },
    {
        "id": "dt6",
        "title": "Space Force is a Waste of Money",
        "description": "Former Air Force general calls Space Force unnecessary bureaucracy",
        "start_time_seconds": 1234.1,
        "end_time_seconds": 1289.6,
        "transcript_text": "Space Force is the biggest military boondoggle since the F-35. We already had space capabilities in the Air Force. Now we're duplicating infrastructure, creating new bureaucracies, and wasting billions on a vanity project. Meanwhile, China is actually building space weapons while we're busy making new uniforms.",
        "tags": ["space-force", "military-bureaucracy", "waste", "air-force"],
        "best_votes": 1456,
        "worst_votes": 2134,
        "vote_score": -678,
        "controversy_score": 0.59,
        "is_featured": False,
        "created_at": "2025-05-20T15:45:00Z",
        "episode_title": "Space Domain Challenges",
        "podcast_name": "Horns of a Dilemma"
    },
    {
        "id": "dt7",
        "title": "Silicon Valley Doesn't Understand War",
        "description": "Pentagon tech advisor slams tech companies working on defense",
        "start_time_seconds": 2456.7,
        "end_time_seconds": 2512.3,
        "transcript_text": "These Silicon Valley kids think war is a coding problem you can disrupt with apps. They've never seen combat, never held a rifle, never had to make life-or-death decisions under fire. Yet they want to build our weapons systems? War isn't about elegant code - it's about brutal, reliable systems that work when everything goes wrong.",
        "tags": ["silicon-valley", "defense-tech", "military-culture", "tech-companies"],
        "best_votes": 2876,
        "worst_votes": 567,
        "vote_score": 2309,
        "controversy_score": 0.16,
        "is_featured": True,
        "created_at": "2025-05-19T13:30:00Z",
        "episode_title": "Tech Meets Defense",
        "podcast_name": "Valley of Depth"
    },
    {
        "id": "dt8",
        "title": "Drone Swarms Will End Aircraft Carriers",
        "description": "Naval strategist predicts carrier obsolescence within a decade",
        "start_time_seconds": 3456.2,
        "end_time_seconds": 3523.8,
        "transcript_text": "Aircraft carriers are floating coffins in the age of hypersonic missiles and drone swarms. One Chinese drone swarm costs $10 million and can sink a $13 billion carrier. We're building these massive targets while our enemies are building the weapons to destroy them. The age of naval aviation is over.",
        "tags": ["aircraft-carriers", "drone-swarms", "naval-warfare", "china"],
        "best_votes": 1234,
        "worst_votes": 3456,
        "vote_score": -2222,
        "controversy_score": 0.74,
        "is_featured": True,
        "created_at": "2025-05-18T10:15:00Z",
        "episode_title": "Future of Naval Power",
        "podcast_name": "All Quiet on the Second Front"
    },
    {
        "id": "dt9",
        "title": "The Military-Industrial Complex Controls Congress",
        "description": "Eisenhower's warning proven true by defense spending analysis",
        "start_time_seconds": 1789.4,
        "end_time_seconds": 1856.7,
        "transcript_text": "Eisenhower warned us about the military-industrial complex, and we ignored him. Defense contractors have a facility in every congressional district by design. They spend more on lobbying than most countries spend on their entire military. Congress doesn't oversee defense spending - defense contractors oversee Congress.",
        "tags": ["military-industrial-complex", "congress", "lobbying", "eisenhower"],
        "best_votes": 4567,
        "worst_votes": 234,
        "vote_score": 4333,
        "controversy_score": 0.05,
        "is_featured": True,
        "created_at": "2025-05-17T16:20:00Z",
        "episode_title": "Defense Budget Politics",
        "podcast_name": "Irregular Warfare Podcast"
    },
    {
        "id": "dt10",
        "title": "America Lost the Afghanistan War in 2003",
        "description": "Counter-insurgency expert explains why mission creep doomed the war",
        "start_time_seconds": 4567.1,
        "end_time_seconds": 4634.8,
        "transcript_text": "We lost Afghanistan the moment we decided to nation-build instead of just killing terrorists. The mission was Al-Qaeda, not democracy. But the Pentagon needed a big war to justify big budgets, so they expanded the mission until it was impossible. Twenty years and $2 trillion later, the Taliban is back in power.",
        "tags": ["afghanistan", "nation-building", "mission-creep", "pentagon"],
        "best_votes": 3456,
        "worst_votes": 1234,
        "vote_score": 2222,
        "controversy_score": 0.26,
        "is_featured": False,
        "created_at": "2025-05-16T14:10:00Z",
        "episode_title": "Lessons from Afghanistan",
        "podcast_name": "School of War"
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
