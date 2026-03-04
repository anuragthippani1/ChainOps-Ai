import motor.motor_asyncio
import os
from typing import List, Dict, Any, Optional
from models.schemas import RiskReport, Session
from datetime import datetime
import json

class MongoDBClient:
    def __init__(self):
        # MongoDB connection string - using local MongoDB or MongoDB Atlas free tier
        self.connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/chainops_ai")
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
            self.db = self.client.chainops_ai
            
            # Create indexes for better performance
            await self.db.reports.create_index("report_id", unique=True)
            await self.db.reports.create_index("session_id")
            await self.db.reports.create_index("created_at")
            
            # Create indexes for sessions
            await self.db.sessions.create_index("session_id", unique=True)
            await self.db.sessions.create_index("is_active")
            await self.db.sessions.create_index("created_at")

            # Supply chain news collection
            await self.db.supply_chain_news.create_index("alert_id", unique=True)
            await self.db.supply_chain_news.create_index("published_at")
            
            print("Connected to MongoDB successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            # Fallback to in-memory storage
            self.client = None
            self.db = None
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def store_report(self, report: RiskReport):
        """Store a risk report in the database"""
        try:
            print(f"Storing report {report.report_id}, database available: {self.db is not None}")
            # Temporarily force file storage to debug the issue
            print("Using file storage for debugging")
            await self._store_report_to_file(report)
            print(f"Report stored to file: {report.report_id}")
                
        except Exception as e:
            print(f"Error storing report: {str(e)}")
            # Fallback to file storage
            await self._store_report_to_file(report)
    
    async def get_report(self, report_id: str) -> Optional[RiskReport]:
        """Get a specific report by ID"""
        try:
            if self.db is not None:
                report_dict = await self.db.reports.find_one({"report_id": report_id})
                if report_dict:
                    # Remove MongoDB's _id field
                    report_dict.pop("_id", None)
                    return RiskReport(**report_dict)
            
            # Always fall back to file storage if not found in DB
            print(f"Report not in MongoDB, checking file storage...")
            return await self._get_report_from_file(report_id)
                
        except Exception as e:
            print(f"Error getting report: {str(e)}")
            # Try file storage as last resort
            return await self._get_report_from_file(report_id)
    
    async def get_all_reports(self) -> List[Dict[str, Any]]:
        """Get all reports (for reports page)"""
        try:
            print(f"Database connection status: {self.db is not None}")
            # Temporarily force file storage to debug the issue
            print("Using file storage for debugging")
            return await self._get_all_reports_from_files()
                
        except Exception as e:
            print(f"Error getting all reports: {str(e)}")
            return []
    
    async def _store_report_to_file(self, report: RiskReport):
        """Fallback: Store report to file"""
        import os
        reports_dir = "reports_data"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        filepath = os.path.join(reports_dir, f"{report.report_id}.json")
        with open(filepath, 'w') as f:
            json.dump(report.dict(), f, default=str, indent=2)
    
    async def _get_report_from_file(self, report_id: str) -> Optional[RiskReport]:
        """Fallback: Get report from file"""
        import os
        # Use absolute path to match _get_all_reports_from_files
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports_data")
        filepath = os.path.join(reports_dir, f"{report_id}.json")
        
        print(f"Looking for report file: {filepath}")
        if os.path.exists(filepath):
            print(f"✅ Found report file: {filepath}")
            with open(filepath, 'r') as f:
                report_dict = json.load(f)
                return RiskReport(**report_dict)
        else:
            print(f"❌ Report file not found: {filepath}")
        return None
    
    async def _get_all_reports_from_files(self) -> List[Dict[str, Any]]:
        """Fallback: Get all reports from files"""
        import os
        import glob
        # Use absolute path to ensure we're looking in the right directory
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports_data")
        reports = []
        
        print(f"Looking for reports in: {reports_dir}")
        if os.path.exists(reports_dir):
            for filepath in glob.glob(os.path.join(reports_dir, "*.json")):
                print(f"Found report file: {filepath}")
                with open(filepath, 'r') as f:
                    report_dict = json.load(f)
                    reports.append(report_dict)
        
        print(f"Loaded {len(reports)} reports from files")
        # Sort by creation date
        reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return reports
    
    # Session Management Methods
    async def create_session(self, session: Session) -> bool:
        """Create a new session"""
        try:
            if self.db is not None:
                session_dict = session.dict()
                session_dict["_id"] = session.session_id
                
                await self.db.sessions.replace_one(
                    {"session_id": session.session_id}, 
                    session_dict, 
                    upsert=True
                )
                print(f"Session created: {session.session_id}")
                return True
            else:
                # Fallback to file storage
                await self._store_session_to_file(session)
                return True
                
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a specific session by ID"""
        try:
            if self.db is not None:
                session_dict = await self.db.sessions.find_one({"session_id": session_id})
                if session_dict:
                    session_dict.pop("_id", None)
                    return Session(**session_dict)
            else:
                # Fallback to file storage
                return await self._get_session_from_file(session_id)
                
        except Exception as e:
            print(f"Error getting session: {str(e)}")
            return None
    
    async def get_all_sessions(self) -> List[Session]:
        """Get all sessions"""
        try:
            if self.db is not None:
                sessions = []
                async for session in self.db.sessions.find().sort("created_at", -1):
                    session.pop("_id", None)
                    sessions.append(Session(**session))
                return sessions
            else:
                # Fallback to file storage
                return await self._get_all_sessions_from_files()
                
        except Exception as e:
            print(f"Error getting all sessions: {str(e)}")
            return []
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update a session"""
        try:
            if self.db is not None:
                updates["updated_at"] = datetime.utcnow()
                result = await self.db.sessions.update_one(
                    {"session_id": session_id}, 
                    {"$set": updates}
                )
                return result.modified_count > 0
            else:
                # Fallback to file storage
                return await self._update_session_in_file(session_id, updates)
                
        except Exception as e:
            print(f"Error updating session: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            if self.db is not None:
                result = await self.db.sessions.delete_one({"session_id": session_id})
                return result.deleted_count > 0
            else:
                # Fallback to file storage
                return await self._delete_session_from_file(session_id)
                
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return False
    
    async def get_session_report_count(self, session_id: str) -> int:
        """Get the number of reports for a session"""
        try:
            if self.db is not None:
                count = await self.db.reports.count_documents({"session_id": session_id})
                return count
            else:
                # Fallback to file storage
                return await self._get_session_report_count_from_files(session_id)
                
        except Exception as e:
            print(f"Error getting session report count: {str(e)}")
            return 0

    # Chat persistence (simple transcript per session)
    async def append_chat_message(self, session_id: str, message: Dict[str, Any]) -> None:
        try:
            if self.db is not None:
                await self.db.chats.update_one(
                    {"session_id": session_id},
                    {"$push": {"messages": message}, "$setOnInsert": {"session_id": session_id}},
                    upsert=True,
                )
            else:
                await self._append_chat_message_to_file(session_id, message)
        except Exception as e:
            print(f"Error appending chat message: {e}")
            await self._append_chat_message_to_file(session_id, message)

    async def get_chat_messages(self, session_id: str) -> List[Dict[str, Any]]:
        try:
            if self.db is not None:
                doc = await self.db.chats.find_one({"session_id": session_id})
                return (doc or {}).get("messages", [])
            else:
                return await self._get_chat_messages_from_file(session_id)
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []

    async def _append_chat_message_to_file(self, session_id: str, message: Dict[str, Any]) -> None:
        import os
        chats_dir = "sessions_data"
        if not os.path.exists(chats_dir):
            os.makedirs(chats_dir)
        filepath = os.path.join(chats_dir, f"{session_id}_chat.json")
        transcript: List[Dict[str, Any]] = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    transcript = json.load(f)
                except Exception:
                    transcript = []
        transcript.append(message)
        with open(filepath, "w") as f:
            json.dump(transcript, f, default=str, indent=2)

    async def _get_chat_messages_from_file(self, session_id: str) -> List[Dict[str, Any]]:
        import os
        filepath = os.path.join("sessions_data", f"{session_id}_chat.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []
    
    # File storage fallback methods for sessions
    async def _store_session_to_file(self, session: Session):
        """Fallback: Store session to file"""
        import os
        sessions_dir = "sessions_data"
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
        
        filepath = os.path.join(sessions_dir, f"{session.session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(session.dict(), f, default=str, indent=2)
    
    async def _get_session_from_file(self, session_id: str) -> Optional[Session]:
        """Fallback: Get session from file"""
        import os
        sessions_dir = "sessions_data"
        filepath = os.path.join(sessions_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                session_dict = json.load(f)
                return Session(**session_dict)
        return None
    
    async def _get_all_sessions_from_files(self) -> List[Session]:
        """Fallback: Get all sessions from files"""
        import os
        import glob
        sessions_dir = "sessions_data"
        sessions = []
        
        if os.path.exists(sessions_dir):
            for filepath in glob.glob(os.path.join(sessions_dir, "*.json")):
                with open(filepath, 'r') as f:
                    session_dict = json.load(f)
                    sessions.append(Session(**session_dict))
        
        # Sort by creation date
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        return sessions
    
    async def _update_session_in_file(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Fallback: Update session in file"""
        import os
        sessions_dir = "sessions_data"
        filepath = os.path.join(sessions_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                session_dict = json.load(f)
            
            session_dict.update(updates)
            
            with open(filepath, 'w') as f:
                json.dump(session_dict, f, default=str, indent=2)
            return True
        return False
    
    async def _delete_session_from_file(self, session_id: str) -> bool:
        """Fallback: Delete session from file"""
        import os
        sessions_dir = "sessions_data"
        filepath = os.path.join(sessions_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    # Supply chain news (real-time disruption alerts)
    async def store_supply_chain_news(self, alert) -> bool:
        """Store a supply chain news alert. Uses file fallback if MongoDB unavailable."""
        try:
            if self.db is not None:
                doc = alert.dict() if hasattr(alert, "dict") else alert.model_dump()
                await self.db.supply_chain_news.update_one(
                    {"source_url": doc["source_url"]},
                    {"$set": doc},
                    upsert=True,
                )
                return True
            await self._store_news_to_file(alert)
            return True
        except Exception as e:
            print(f"Error storing supply chain news: {e}")
            await self._store_news_to_file(alert)
            return True

    async def get_supply_chain_news_last_24h(self) -> List[Dict[str, Any]]:
        """Get supply chain news from last 24 hours."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        cutoff_str = cutoff.isoformat()
        try:
            if self.db is not None:
                cursor = self.db.supply_chain_news.find(
                    {"published_at": {"$gte": cutoff_str}}
                ).sort("published_at", -1).limit(50)
                items = []
                async for doc in cursor:
                    doc.pop("_id", None)
                    items.append(doc)
                return items
            return await self._get_news_from_files(cutoff_str)
        except Exception as e:
            print(f"Error getting supply chain news: {e}")
            return await self._get_news_from_files(cutoff_str)

    async def _store_news_to_file(self, alert):
        import os
        import hashlib
        news_dir = os.path.join(os.path.dirname(__file__), "..", "news_data")
        if not os.path.exists(news_dir):
            os.makedirs(news_dir)
        doc = alert.dict() if hasattr(alert, "dict") else alert.model_dump()
        url = doc.get("source_url", "")
        safe_id = hashlib.md5(url.encode() if url else b"").hexdigest()[:16]
        filepath = os.path.join(news_dir, f"{safe_id}.json")
        with open(filepath, "w") as f:
            json.dump(doc, f, default=str, indent=2)

    async def _get_news_from_files(self, cutoff_str: str) -> List[Dict[str, Any]]:
        import os
        import glob
        news_dir = os.path.join(os.path.dirname(__file__), "..", "news_data")
        items = []
        if os.path.exists(news_dir):
            for fp in glob.glob(os.path.join(news_dir, "*.json")):
                try:
                    with open(fp, "r") as f:
                        doc = json.load(f)
                        if doc.get("published_at", "") >= cutoff_str:
                            items.append(doc)
                except Exception:
                    pass
        items.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return items[:50]

    async def _get_session_report_count_from_files(self, session_id: str) -> int:
        """Fallback: Get session report count from files"""
        import os
        import glob
        reports_dir = "reports_data"
        count = 0
        
        if os.path.exists(reports_dir):
            for filepath in glob.glob(os.path.join(reports_dir, "*.json")):
                with open(filepath, 'r') as f:
                    report_dict = json.load(f)
                    if report_dict.get('session_id') == session_id:
                        count += 1
        return count
