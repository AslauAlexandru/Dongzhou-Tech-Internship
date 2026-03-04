# main.py - Runnable Demo
#!/usr/bin/env python3
import asyncio
import sys
import os
from dotenv import load_dotenv
from outreach_system import OutreachStateMachine

load_dotenv()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <company> [domain]")
        print("Example: python main.py Stripe 'ML Platform'")
        return
    
    company = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else "Engineering"
    
    print(f"🚀 OLLAMA Outreach: {company} ({domain})")
    print("💻 100% FREE / OFFLINE\n")
    
    fsm = OutreachStateMachine(
        company_name=company,
        technical_domain=domain,
        ollama_base_url=os.getenv("OLLAMA_BASE_URL"),
        ollama_model=os.getenv("OLLAMA_MODEL")
    )
    
    await fsm.run_campaign()
    print("\n🎉 SUCCESS - Zero cost!")

if __name__ == "__main__":
    asyncio.run(main())





"""
#Gemini
import os
import asyncio
from outreach_system import OutreachStateMachine
from dotenv import load_dotenv

load_dotenv()

async def demo():
    fsm = OutreachStateMachine(
        company_name="Stripe",
        technical_domain="ML Platform",
        target_title="Director",
        gemini_api_key=os.getenv("GEMINI_API_KEY") #openai_api_key="your-key-here"
    )
    
    await fsm.run_campaign()
    print("\n🎉 Campaign completed!")

if __name__ == "__main__":
    asyncio.run(demo())

"""

"""

# Update main.py demo call
async def demo():
    fsm = OutreachStateMachine(
        company_name="Stripe",
        technical_domain="ML Platform", 
        target_title="Director",
        gemini_api_key=os.getenv("GEMINI_API_KEY")  # Free key
    )

"""

"""

# main.py - Works with FREE Gemini
import asyncio
from outreach_system import OutreachStateMachine
from dotenv import load_dotenv

load_dotenv()

async def main():
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "Stripe"
    domain = sys.argv[2] if len(sys.argv) > 2 else "ML Platform"
    
    print(f"🚀 Outreach demo: {company} ({domain})")
    print("Using FREE Google Gemini API\n")
    
    fsm = OutreachStateMachine(company, domain)
    await fsm.run_campaign()

if __name__ == "__main__":
    asyncio.run(main())

# Run Demo (Zero Cost)
# pip install google-generativeai
# echo "GEMINI_API_KEY=AIza..." > .env
# python main.py Stripe "ML Platform"

"""