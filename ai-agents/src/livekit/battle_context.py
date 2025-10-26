"""
Battle Context Manager - Aggregates real-time battle state for commentator
Provides rich context snapshots to enable intelligent voice commentary
"""

import asyncio
import time
import copy
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class BattleEvent:
    """Represents a battle event"""
    event_type: str
    data: Dict[str, Any]
    timestamp: float
    message: str

class BattleContextManager:
    """Central source of truth for battle state - thread-safe context aggregation"""
    
    def __init__(self):
        self.state = {
            "project_id": None,
            "project_description": None,
            "current_round": 0,
            "current_subtask": None,
            "agents_progress": {},
            "round_winners": [],
            "agent_stats": {},
            "recent_events": [],
            "battle_start_time": None,
            "total_rounds": 0
        }
        self._lock = asyncio.Lock()
    
    async def initialize_battle(self, project_id: str, project_description: str, total_rounds: int = 4):
        """Initialize a new battle"""
        async with self._lock:
            self.state = {
                "project_id": project_id,
                "project_description": project_description,
                "current_round": 0,
                "current_subtask": None,
                "agents_progress": {},
                "round_winners": [],
                "agent_stats": {},
                "recent_events": [],
                "battle_start_time": time.time(),
                "total_rounds": total_rounds
            }
            
            # Initialize agent stats
            for agent_name in ["One", "Two", "Three", "Four"]:
                self.state["agent_stats"][agent_name] = {
                    "wins": 0,
                    "total_rounds": 0,
                    "avg_completion_time": 0,
                    "personality": self._get_agent_personality(agent_name)
                }
            
            await self._add_event("battle_start", f"Battle started: {project_description}")
    
    async def update_round_start(self, subtask_title: str, subtask_description: str, round_num: int):
        """Called when a new round starts"""
        async with self._lock:
            self.state["current_round"] = round_num
            self.state["current_subtask"] = {
                "title": subtask_title,
                "description": subtask_description,
                "round_num": round_num,
                "start_time": time.time()
            }
            
            # Reset agent progress for new round
            self.state["agents_progress"] = {}
            
            await self._add_event("round_start", f"Round {round_num}: {subtask_title}")
    
    async def update_agent_progress(self, agent_name: str, progress_message: str):
        """Called when an agent makes progress"""
        async with self._lock:
            if agent_name not in self.state["agents_progress"]:
                self.state["agents_progress"][agent_name] = []
            
            progress_entry = {
                "message": progress_message,
                "timestamp": time.time(),
                "status": "working"
            }
            
            self.state["agents_progress"][agent_name].append(progress_entry)
            
            await self._add_event("agent_progress", f"{agent_name}: {progress_message}")
    
    async def update_agent_completion(self, agent_name: str, work_result: Dict[str, Any]):
        """Called when an agent completes their work"""
        async with self._lock:
            if agent_name not in self.state["agents_progress"]:
                self.state["agents_progress"][agent_name] = []
            
            completion_entry = {
                "status": "completed",
                "code_lines": len(work_result.get("code", "").split('\n')),
                "timestamp": time.time(),
                "completion_time": time.time() - self.state["current_subtask"]["start_time"]
            }
            
            self.state["agents_progress"][agent_name].append(completion_entry)
            
            # Update agent stats
            if agent_name in self.state["agent_stats"]:
                self.state["agent_stats"][agent_name]["total_rounds"] += 1
                # Update average completion time
                current_avg = self.state["agent_stats"][agent_name]["avg_completion_time"]
                total_rounds = self.state["agent_stats"][agent_name]["total_rounds"]
                new_avg = ((current_avg * (total_rounds - 1)) + completion_entry["completion_time"]) / total_rounds
                self.state["agent_stats"][agent_name]["avg_completion_time"] = new_avg
            
            await self._add_event("agent_complete", f"{agent_name} completed their work!")
    
    async def update_winner(self, winner_name: str, reason: str, user_explanation: str = ""):
        """Called when a winner is selected"""
        async with self._lock:
            winner_data = {
                "winner": winner_name,
                "reason": reason,
                "user_explanation": user_explanation,
                "round": self.state["current_round"],
                "timestamp": time.time()
            }
            
            self.state["round_winners"].append(winner_data)
            
            # Update agent stats
            if winner_name in self.state["agent_stats"]:
                self.state["agent_stats"][winner_name]["wins"] += 1
            
            await self._add_event("winner_selected", f"{winner_name} wins Round {self.state['current_round']}!")
    
    async def _add_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Add event to timeline"""
        event = BattleEvent(
            event_type=event_type,
            data=data or {},
            timestamp=time.time(),
            message=message
        )
        
        self.state["recent_events"].append(event)
        
        # Keep only last 20 events to prevent memory bloat
        if len(self.state["recent_events"]) > 20:
            self.state["recent_events"] = self.state["recent_events"][-20:]
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get current battle state snapshot (thread-safe copy)"""
        return copy.deepcopy(self.state)
    
    def get_context_summary(self) -> str:
        """Get formatted context summary for commentator"""
        snapshot = self.get_snapshot()
        
        summary = f"""
CURRENT BATTLE STATE:
- Project: {snapshot['project_description']}
- Round: {snapshot['current_round']}/{snapshot['total_rounds']}
- Current Subtask: {snapshot['current_subtask']['title'] if snapshot['current_subtask'] else 'None'}
- Description: {snapshot['current_subtask']['description'] if snapshot['current_subtask'] else 'None'}

AGENT PROGRESS:
{self._format_agent_progress(snapshot)}

LEADERBOARD:
{self._format_leaderboard(snapshot)}

RECENT EVENTS:
{self._format_recent_events(snapshot, 5)}

BATTLE STATS:
- Duration: {self._format_duration(snapshot)}
- Agents Working: {len([a for a in snapshot['agents_progress'].values() if a and a[-1]['status'] == 'working'])}
- Agents Complete: {len([a for a in snapshot['agents_progress'].values() if a and a[-1]['status'] == 'completed'])}
"""
        return summary.strip()
    
    def _format_agent_progress(self, snapshot: Dict[str, Any]) -> str:
        """Format agent progress for context"""
        progress_lines = []
        
        for agent_name, progress_list in snapshot["agents_progress"].items():
            if progress_list:
                latest = progress_list[-1]
                status = latest["status"]
                
                if status == "completed":
                    lines = latest.get("code_lines", 0)
                    time_taken = latest.get("completion_time", 0)
                    progress_lines.append(f"- {agent_name}: ✅ Completed ({lines} lines, {time_taken:.1f}s)")
                else:
                    message = latest.get("message", "Working...")
                    progress_lines.append(f"- {agent_name}: 🔄 {message}")
            else:
                progress_lines.append(f"- {agent_name}: ⏳ Not started")
        
        return "\n".join(progress_lines) if progress_lines else "No progress yet"
    
    def _format_leaderboard(self, snapshot: Dict[str, Any]) -> str:
        """Format leaderboard for context"""
        stats = snapshot["agent_stats"]
        if not stats:
            return "No stats yet"
        
        # Sort by wins
        sorted_agents = sorted(stats.items(), key=lambda x: x[1]["wins"], reverse=True)
        
        leaderboard_lines = []
        for agent_name, data in sorted_agents:
            wins = data["wins"]
            total_rounds = data["total_rounds"]
            win_rate = (wins / total_rounds * 100) if total_rounds > 0 else 0
            leaderboard_lines.append(f"- {agent_name}: {wins} wins ({win_rate:.0f}% win rate)")
        
        return "\n".join(leaderboard_lines)
    
    def _format_recent_events(self, snapshot: Dict[str, Any], limit: int = 5) -> str:
        """Format recent events"""
        events = snapshot["recent_events"][-limit:]
        event_lines = []
        
        for event in events:
            timestamp = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
            event_lines.append(f"- [{timestamp}] {event.message}")
        
        return "\n".join(event_lines) if event_lines else "No recent events"
    
    def _format_duration(self, snapshot: Dict[str, Any]) -> str:
        """Format battle duration"""
        if not snapshot["battle_start_time"]:
            return "Unknown"
        
        duration = time.time() - snapshot["battle_start_time"]
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}m {seconds}s"
    
    def _get_agent_personality(self, agent_name: str) -> str:
        """Get agent personality description"""
        personalities = {
            "One": "Sarcastic, funny, loves memes, writes clean code with humor",
            "Two": "Technical perfectionist, loves documentation, over-engineers everything",
            "Three": "Fast-paced, aggressive, loves performance, ships quickly",
            "Four": "Creative, design-focused, loves beautiful UI, user-centric"
        }
        return personalities.get(agent_name, "Unknown personality")
    
    def get_agent_personality(self, agent_name: str) -> str:
        """Get agent personality from current state"""
        return self.state["agent_stats"].get(agent_name, {}).get("personality", "Unknown")
    
    def get_current_round_info(self) -> Dict[str, Any]:
        """Get current round information"""
        return {
            "round": self.state["current_round"],
            "subtask": self.state["current_subtask"],
            "total_rounds": self.state["total_rounds"],
            "progress_percentage": (self.state["current_round"] / self.state["total_rounds"] * 100) if self.state["total_rounds"] > 0 else 0
        }
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get specific agent status"""
        progress = self.state["agents_progress"].get(agent_name, [])
        stats = self.state["agent_stats"].get(agent_name, {})
        
        return {
            "name": agent_name,
            "personality": stats.get("personality", "Unknown"),
            "wins": stats.get("wins", 0),
            "total_rounds": stats.get("total_rounds", 0),
            "current_status": progress[-1]["status"] if progress else "not_started",
            "latest_message": progress[-1]["message"] if progress else None,
            "avg_completion_time": stats.get("avg_completion_time", 0)
        }
