import eai_http_middleware
import os

os.environ['TAVILY_API_KEY'] = 'fake-key'
os.environ['OPENAI_BASE_URL'] = os.getenv("LLM_BASE_URL")
os.environ['OPENAI_API_KEY'] = os.getenv("LLM_API_KEY")

from backend.report_type import DetailedReport
from gpt_researcher.utils.enum import Tone
from gpt_researcher import GPTResearcher

async def prompt(messages: list[dict[str, str]], **kwargs) -> str:
    query_domains = kwargs.get("query_domains", "")
    report_type = kwargs.get("report_type", "") 
    tone =  kwargs.get("tone", "formal")

    query_domains = query_domains.split(",") if query_domains else []
    
    assert len(messages) > 0, "received empty messages"
    query = messages[-1]['content']

    if report_type == 'detailed_report':
        detailed_report = DetailedReport(
            query=query,
            query_domains=query_domains,
            report_type="research_report",
            report_source="web_search",
        )

        report = await detailed_report.run()
    else:
        # Convert the simple keyword to the full Tone enum value
        tone_map = {
            "objective": Tone.Objective,
            "formal": Tone.Formal,
            "analytical": Tone.Analytical,
            "persuasive": Tone.Persuasive,
            "informative": Tone.Informative,
            "explanatory": Tone.Explanatory,
            "descriptive": Tone.Descriptive,
            "critical": Tone.Critical,
            "comparative": Tone.Comparative,
            "speculative": Tone.Speculative,
            "reflective": Tone.Reflective,
            "narrative": Tone.Narrative,
            "humorous": Tone.Humorous,
            "optimistic": Tone.Optimistic,
            "pessimistic": Tone.Pessimistic
        }

        researcher = GPTResearcher(
            query=query,
            query_domains=query_domains,
            report_type=report_type,
            tone=tone_map[tone]
        )

        await researcher.conduct_research()

        report = await researcher.write_report()
        
    return report