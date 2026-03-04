# outreach_system.py - Core State Machine
import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import openai
from transitions import Machine
import os
from pathlib import Path
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
                 target_title: str = "Director", openai_api_key: str = None):
        self.company_name = company_name
        self.domain = technical_domain
        self.target_title = target_title
        self.decision_maker: Optional[DecisionMaker] = None
        self.linkedin_message: str = ""
        self.followup_message: str = ""
        self.meeting_link: str = ""
        
        # State persistence
        self.state_file = Path(f"campaign_{company_name.lower().replace(' ', '_')}.json")
        
        # LLM Setup
        openai.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize FSM
        self.machine = Machine(
            model=self,
            states=OutreachState,
            initial=OutreachState.INITIALIZED,
            send_event=True
        )
        
        self._setup_transitions()
        self._load_state()
    
    def _setup_transitions(self):
        """Define all possible state transitions"""
        self.machine.add_transition(
            trigger='find_decision_maker', source='*', dest='decision_maker_found'
        )
        self.machine.add_transition(
            trigger='send_connection', source='decision_maker_found', dest='connection_sent'
        )
        self.machine.add_transition(
            trigger='connection_accepted', source='connection_sent', dest='connection_accepted'
        )
        self.machine.add_transition(
            trigger='send_followup', source='connection_accepted', dest='followup_sent'
        )
        self.machine.add_transition(
            trigger='receive_reply', source='followup_sent', dest='reply_received'
        )
        self.machine.add_transition(
            trigger='create_meeting', source='reply_received', dest='meeting_created'
        )
        self.machine.add_transition(
            trigger='complete', source='meeting_created', dest='completed'
        )
        self.machine.add_transition(
            trigger='fail', source='*', dest='failed'
        )
    
    async def find_decision_maker(self) -> bool:
        """Mock company lookup + LLM-powered decision maker identification"""
        print(f"🔍 Searching for {self.target_title} at {self.company_name} ({self.domain})")
        
        # Mock external API call (replace with Apollo.io, Clearbit, etc.)
        await asyncio.sleep(1)
        
        mock_profiles = {
            "Stripe": ["Sarah Chen", "David Patel", "Maria Gonzalez"],
            "Airbnb": ["Raj Singh", "Emily Wu"],
            "Snowflake": ["Michael Chen", "Priya Sharma"]
        }
        
        profiles = mock_profiles.get(self.company_name, ["John Doe"])
        selected = profiles[0]  # Deterministic for demo
        
        prompt = f"""
        Given company: {self.company_name}, domain: {self.domain}
        Select best decision maker from: {profiles}
        Return ONLY the name of the most senior relevant person.
        """
        
        response = await self._call_llm(prompt)
        self.decision_maker = DecisionMaker(
            name=selected,
            title=f"{self.target_title} of {self.domain}",
            linkedin_url=f"https://linkedin.com/in/{selected.lower().replace(' ', '-')}",
            company=self.company_name,
            domain_experience="5+ years leading platform teams"
        )
        
        print(f"✅ Found: {self.decision_maker.name}, {self.decision_maker.title}")
        self.save_state()
        return True
    
    async def generate_linkedin_message(self) -> str:
        """Generate personalized LinkedIn connection request"""
        prompt = f"""
        Write a LinkedIn connection request (MAX 300 chars) to {self.decision_maker.name}
        Context: {self.company_name}, {self.domain}. Be specific, reference their work.
        Professional but warm. NO sales pitch.
        
        Examples:
        "Hi Sarah, loved your recent post on scalable ML infra at Stripe..."
        "David - your work on {self.domain} at {self.company_name} caught my eye..."
        """
        
        self.linkedin_message = await self._call_llm(prompt)
        return self.linkedin_message
    
    async def send_connection_request(self):
        """Mock LinkedIn API call"""
        print(f"📝 Generated LinkedIn message ({len(self.linkedin_message)} chars):")
        print(f"   {self.linkedin_message[:100]}...")
        print("🚀 [MOCK] Sending connection request via LinkedIn API...")
        await asyncio.sleep(1)
        print("✅ Connection request sent!")
    
    async def wait_for_acceptance(self, max_wait_hours: int = 48):
        """Mock waiting period with realistic timing"""
        print(f"⏳ [MOCK] Waiting for connection acceptance (max {max_wait_hours}h)...")
        await asyncio.sleep(2)
        print("✓ Accepted after 2h 15m")
        return True
    
    async def generate_followup(self) -> str:
        """Generate polite follow-up message"""
        prompt = f"""
        Follow-up LinkedIn message to {self.decision_maker.name} after connection accepted.
        Ask for 15-min intro call. Reference connection request.
        Keep conversational, time-box the ask.
        
        Example: "Thanks for connecting Sarah! Would you have 15min next week..."
        """
        self.followup_message = await self._call_llm(prompt)
        return self.followup_message
    
    async def send_followup(self):
        print(f"📨 Generated follow-up ({len(self.followup_message)} chars):")
        print(f"   {self.followup_message[:100]}...")
        print("🚀 [MOCK] Sending follow-up message...")
        await asyncio.sleep(1)
        print("✅ Follow-up sent!")
    
    async def wait_for_reply(self, max_wait_hours: int = 72):
        """Mock reply with 85% positive response rate"""
        print(f"⏳ [MOCK] Waiting for reply (max {max_wait_hours}h)...")
        await asyncio.sleep(2)
        self.reply = "Yes, happy to chat next week!"
        print(f"✓ Reply: {self.reply}")
        return True
    
    async def create_teams_meeting(self):
        """Generate realistic Teams meeting link"""
        start_time = datetime.now() + timedelta(days=3)
        self.meeting_link = (
            f"https://teams.microsoft.com/l/meetup-"
            f"{start_time.strftime('%Y%m%dT%H%M')}/"
            f"IntroCall_{self.company_name}_{self.domain.replace(' ', '')}"
        )
        print(f"🔗 Generated Teams meeting: {self.meeting_link}")
        print("🎉 Outreach completed successfully!")
    
    async def _call_llm(self, prompt: str) -> str:
        """Structured LLM call with caching"""
        cache_key = hash(prompt) % 1000
        cache_file = Path(f"cache_{cache_key}.txt")
        
        if cache_file.exists():
            return cache_file.read_text()
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3  # Deterministic
        )
        
        result = response.choices[0].message.content.strip()
        cache_file.write_text(result)
        return result
    
    def save_state(self):
        state_data = {
            "current_state": self.state,
            "decision_maker": vars(self.decision_maker) if self.decision_maker else None,
            "messages": {
                "linkedin": self.linkedin_message,
                "followup": self.followup_message
            },
            "meeting_link": self.meeting_link,
            "timestamp": datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(state_data, indent=2))
    
    def _load_state(self):
        if self.state_file.exists():
            print(f"📂 Resuming from saved state: {self.state_file}")
            # Implementation for state restoration
    
    async def run_campaign(self):
        """Execute complete workflow"""
        try:
            await self.find_decision_maker()
            self.send_connection(trigger='send_connection')
            await self.generate_linkedin_message()
            await self.send_connection_request()
            await self.wait_for_acceptance()
            self.connection_accepted(trigger='connection_accepted')
            
            await self.generate_followup()
            await self.send_followup()
            self.send_followup(trigger='send_followup')
            
            await self.wait_for_reply()
            self.receive_reply(trigger='receive_reply')
            
            await self.create_teams_meeting()
            self.complete(trigger='complete')
            
        except Exception as e:
            print(f"❌ Campaign failed: {e}")
            self.fail(trigger='fail')

