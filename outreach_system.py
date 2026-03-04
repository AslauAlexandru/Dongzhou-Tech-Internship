# outreach_system.py - Core State Machine
import asyncio
import json
import requests
import ollama
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from transitions import Machine
from dotenv import load_dotenv
load_dotenv()


@dataclass
class DecisionMaker:
    name: str
    title: str
    linkedin_url: str
    company: str
    domain_experience: str

class OutreachState(Enum):
    INITIALIZED = "initialized"
    DECISION_MAKER_FOUND = "decision_maker_found"
    CONNECTION_SENT = "connection_sent"
    CONNECTION_ACCEPTED = "connection_accepted"
    FOLLOWUP_SENT = "followup_sent"
    REPLY_RECEIVED = "reply_received"
    MEETING_CREATED = "meeting_created"
    FAILED = "failed"
    COMPLETED = "completed"

class OutreachStateMachine:
    def __init__(self, company_name: str, technical_domain: str, 
                 target_title: str = "Director", ollama_base_url: str = None, 
                 ollama_model: str = None):
        self.company_name = company_name
        self.domain = technical_domain
        self.target_title = target_title
        self.decision_maker: Optional[DecisionMaker] = None
        self.linkedin_message: str = ""
        self.followup_message: str = ""
        self.meeting_link: str = ""
        self.reply: str = ""
        
        # State persistence
        self.state_file = Path(f"campaign_{company_name.lower().replace(' ', '_')}.json")
        
        # FREE Ollama setup
        #self.ollama_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        #self.model_name = ollama_model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.ollama_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL")
        self.model_name = ollama_model or os.getenv("OLLAMA_MODEL")
        self._health_check()
        
        # Initialize FSM with string state values
        self.machine = Machine(
            model=self,
            states=[s.value for s in OutreachState],
            initial='initialized'
        )
        self._setup_transitions()
        self._load_state()
    
    def _health_check(self):
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            models = response.json()['models']
            print(f"✅ Ollama ready: {len(models)} models")
            print(f"   Using: {self.model_name}")
        except:
            print("⚠️  Starting Ollama... (run: ollama serve)")
    
    def _setup_transitions(self):
        self.machine.add_transition('find_decision_maker', '*', 'decision_maker_found')
        self.machine.add_transition('send_connection', 'decision_maker_found', 'connection_sent')
        self.machine.add_transition('connection_accepted', 'connection_sent', 'connection_accepted')
        self.machine.add_transition('send_followup', 'connection_accepted', 'followup_sent')
        self.machine.add_transition('receive_reply', 'followup_sent', 'reply_received')
        self.machine.add_transition('create_meeting', 'reply_received', 'meeting_created')
        self.machine.add_transition('complete', 'meeting_created', 'completed')
        self.machine.add_transition('fail', '*', 'failed')
    
    async def _execute_find_decision_maker(self) -> bool:
        print(f"🔍 Searching {self.target_title} at {self.company_name} ({self.domain})")
        await asyncio.sleep(1)
        
        mock_profiles = {
            "Stripe": ["Sarah Chen", "David Patel"],
            "Airbnb": ["Raj Singh", "Emily Wu"],
            "Snowflake": ["Michael Chen", "Priya Sharma"],
            "default": ["John Doe"]
        }
        
        profiles = mock_profiles.get(self.company_name, mock_profiles["default"])
        selected = profiles[0]
        
        self.decision_maker = DecisionMaker(
            name=selected,
            title=f"{self.target_title} of {self.domain}",
            linkedin_url=f"https://linkedin.com/in/{selected.lower().replace(' ', '-')}",
            company=self.company_name,
            domain_experience="5+ years leading platform teams"
        )
        
        print(f"✅ Found: {self.decision_maker.name}")
        self.save_state()
        return True
    
    async def generate_linkedin_message(self) -> str:
        prompt = f"""Write LinkedIn connection request (<300 chars) to {self.decision_maker.name}
Company: {self.company_name}, Domain: {self.domain}. Professional, specific, warm. NO sales.

Examples: "Hi Sarah, loved your ML infra work at Stripe..." """
        
        self.linkedin_message = await self._call_llm(prompt)
        return self.linkedin_message
    
    async def send_connection_request(self):
        print(f"📝 LinkedIn message ({len(self.linkedin_message)} chars):")
        print(f"   {self.linkedin_message[:100]}...")
        print("🚀 [MOCK] Sending via LinkedIn API...")
        await asyncio.sleep(1)
        print("✅ Connection sent!")
    
    async def wait_for_acceptance(self):
        print("⏳ [MOCK] Waiting for acceptance (2h 15m)...")
        await asyncio.sleep(2)
        print("✓ Accepted!")
        return True
    
    async def generate_followup(self) -> str:
        prompt = f"""Follow-up message to {self.decision_maker.name} after connection accepted.
Ask for 15min intro call. Conversational, time-boxed ask.

Example: "Thanks Sarah! 15min next week?"""""
        
        self.followup_message = await self._call_llm(prompt)
        return self.followup_message
    
    async def _execute_send_followup(self):
        print(f"📨 Follow-up ({len(self.followup_message)} chars):")
        print(f"   {self.followup_message[:100]}...")
        print("🚀 [MOCK] Sending follow-up...")
        await asyncio.sleep(1)
        print("✅ Follow-up sent!")
    
    async def wait_for_reply(self):
        print("⏳ [MOCK] Waiting for reply...")
        await asyncio.sleep(2)
        self.reply = "Yes, happy to chat next week!"
        print(f"✓ Reply: '{self.reply}'")
        return True
    
    async def create_teams_meeting(self):
        start_time = datetime.now() + timedelta(days=3)
        self.meeting_link = (
            f"https://teams.microsoft.com/l/meetup-"
            f"{start_time.strftime('%Y%m%dT%H%M')}/"
            f"{self.company_name}_{self.domain.replace(' ', '')}"
        )
        print(f"🔗 Teams meeting: {self.meeting_link}")
        print("🎉 Outreach COMPLETED!")
    
    async def _call_llm(self, prompt: str) -> str:
        import hashlib
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_dir = Path(".llm_cache")
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / f"{cache_key}.txt"
        
        if cache_file.exists():
            return cache_file.read_text()
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 200,
                "top_p": 0.8
            }
        }
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            result = response.json()["response"].strip()
            cache_file.write_text(result)
            return result
        except:
            return self._fallback_message(prompt)
    
    def _fallback_message(self, prompt: str) -> str:
        if "connection" in prompt.lower():
            return f"Hi {self.decision_maker.name}, impressed by your {self.domain} work at {self.company_name}."
        return f"Thanks {self.decision_maker.name}! Available for 15min intro call?"
    
    def save_state(self):
        state_data = {
            "state": self.state,  # Already a string
            "decision_maker": vars(self.decision_maker) if self.decision_maker else None,
            "messages": {"linkedin": self.linkedin_message, "followup": self.followup_message},
            "meeting_link": self.meeting_link,
            "timestamp": datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(state_data, indent=2))
    
    def _load_state(self):
        if self.state_file.exists():
            print(f"📂 Resuming: {self.state_file}")
    
    async def run_campaign(self):
        try:
            # Step 1: Find decision maker
            await self._execute_find_decision_maker()
            self.find_decision_maker()  # Trigger state transition
            
            # Step 2: Generate and send LinkedIn message
            await self.generate_linkedin_message()
            await self.send_connection_request()
            self.send_connection()  # Trigger state transition
            
            # Step 3: Wait for connection acceptance
            await self.wait_for_acceptance()
            self.connection_accepted()  # Trigger state transition
            
            # Step 4: Generate and send follow-up
            await self.generate_followup()
            await self._execute_send_followup()
            self.send_followup()  # Trigger state transition
            
            # Step 5: Wait for reply
            await self.wait_for_reply()
            self.receive_reply()  # Trigger state transition
            
            # Step 6: Create meeting and complete
            await self.create_teams_meeting()
            self.create_meeting()  # Trigger state transition
            self.complete()  # Trigger state transition
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.fail()  # Trigger state transition
            self.fail()

