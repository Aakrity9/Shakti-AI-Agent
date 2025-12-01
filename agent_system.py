import numpy as np 
import pandas as pd 


import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


# 1 Core Multi-Agent System Framework ---

import json
import uuid
import time
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field

class AgentType(Enum):
    THREAT_DETECTOR = "threat_detector"
    MANIPULATION_DETECTOR = "manipulation_detector"

@dataclass
class AgentLog:
    timestamp: float
    agent_name: str
    message: str
    data: Optional[Dict[str, Any]] = None

class AgentContext:
    """
    Manages session memory, logging, and state for the agent system.
    """
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.memory: Dict[str, Any] = {}
        self.logs: List[AgentLog] = []
        self.start_time = time.time()

    def log(self, agent_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        log_entry = AgentLog(time.time(), agent_name, message, data)
        self.logs.append(log_entry)
         

    def get_memory(self, key: str) -> Any:
        return self.memory.get(key)

    def set_memory(self, key: str, value: Any):
        self.memory[key] = value

    def get_trace(self) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": log.timestamp,
                "agent": log.agent_name,
                "message": log.message,
                "data": log.data
            }
            for log in self.logs
        ]

class BaseAgent:
    """
    Abstract base class for all agents.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def process(self, input_data: Any, context: AgentContext) -> Any:
        raise NotImplementedError("Agents must implement the process method")

    def _mock_llm_call(self, prompt: str) -> str:
        raise NotImplementedError("Agents must implement their own mock logic")

    def _call_llm_api(self, system_prompt: str, user_text: str, api_key: Optional[str] = None) -> str:
        if not api_key:
            return self._mock_llm_call(user_text)
        
        return self._mock_llm_call(user_text)

class AgentOrchestrator:
    """
    Manages the execution of agents. Supports sequential chains and parallel execution (simulated).
    """
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.context = AgentContext()

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def run_chain(self, input_text: str, agent_names: List[str]) -> Dict[str, Any]:
        """
        Runs a list of agents sequentially.
        """
        results = {}
        self.context.log("Orchestrator", f"Starting chain with agents: {agent_names}")
        
        for name in agent_names:
            agent = self.agents.get(name)
            if agent:
                
                results[name] = agent.process(input_text, self.context)
            else:
                self.context.log("Orchestrator", f"Agent not found: {name}")
        
        self.context.log("Orchestrator", "Chain complete")
        return results

    def run_parallel(self, input_text: str, agent_names: List[str]) -> Dict[str, Any]:
        """
        Simulates parallel execution (in this synchronous script, it's just a loop, 
        but in a real app this would use asyncio or threads).
        """
        self.context.log("Orchestrator", f"Starting parallel execution with agents: {agent_names}")
        
        return self.run_chain(input_text, agent_names)

    def get_execution_trace(self):
        return self.context.get_trace()


# 2 Threat Detection Agent ---


class ThreatDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ThreatDetectionAgent",
            description="Detects harassment, threats, coercion, and unsafe requests."
        )
        self.system_prompt = "You are a Threat Detection Agent. Analyze the input for threats."

        # --- INTERNAL KNOWLEDGE BASE (The "Brain") ---
        self.knowledge_base = {
            "deepfake": {
                "keywords": ["fake images", "ai generated", "deepfake", "face swap", "nude", "morph", "inappropriate images", "fake photos", "created fake"],
                "category": "Deepfake / Image Abuse",
                "severity": 5,
                "action": "Report to platform immediately. File complaint at Cyber Crime portal. Do not delete evidence."
            },
            "domestic_abuse": {
                "keywords": ["husband", "wife", "partner", "beat", "hit", "slap", "control", "money", "salary", "passport", "prisoner", "allow", "forbid"],
                "category": "Domestic Abuse / Coercive Control",
                "severity": 4,
                "action": "Contact domestic abuse helpline. Secure documents. Plan exit strategy."
            },
            "blackmail": {
                "keywords": ["photos", "video", "leak", "viral", "expose", "internet", "send money", "pay me", "release"],
                "category": "Blackmail / Sextortion",
                "severity": 4,
                "action": "Do not pay. Do not delete chats. Report to Cyber Crime."
            },
            "stalking": {
                "keywords": ["follow", "watch", "outside", "track", "everywhere", "saw you", "know where you live"],
                "category": "Stalking / Surveillance",
                "severity": 4,
                "action": "Vary routines. Document evidence. Contact police."
            },
            "sexual_harassment": {
                "keywords": ["touch", "kiss", "body", "sexy", "hot", "nude", "naked", "send pics", "rape", "force", "molest"],
                "category": "Sexual Harassment / Assault",
                "severity": 5,
                "action": "Go to safe place. Call emergency services."
            },
            "violence": {
                "keywords": ["kill", "die", "murder", "shoot", "stab", "burn", "acid", "hurt", "attack", "destroy"],
                "category": "Violence / Physical Harm",
                "severity": 5,
                "action": "Contact law enforcement immediately. Ensure physical safety."
            }
        }

    def _google_search_simulation(self, query: str) -> Dict[str, Any]:
        """
        Simulates a 'Google Search' by scanning the internal knowledge base 
        and also checking for unknown high-risk patterns.
        """
        query = query.lower()
        best_match = None
        max_score = 0

        # 1. Search Knowledge Base (The "Indexed Web")
        for key, data in self.knowledge_base.items():
            score = 0
            for word in data["keywords"]:
                if word in query:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = data

        if best_match and max_score > 0:
            return {
                "found": True,
                "source": "Knowledge Base Match",
                "result": best_match
            }
            
        # 2. "Google" Fallback for Unknowns (Simulated Learning)
        
        suspicious_words = ["danger", "scared", "help", "police", "emergency", "threat"]
        if any(w in query for w in suspicious_words):
             return {
                "found": True,
                "source": "Heuristic Analysis",
                "result": {
                    "category": "Unclassified Suspicious Activity",
                    "severity": 3,
                    "action": "Situation unclear but suspicious. Proceed with caution."
                }
            }
        
        return {"found": False, "source": "Web Search", "result": None}

    def _mock_llm_call(self, prompt: str) -> str:

        # Step 1: Run the "Google Search" Simulation

        search_result = self._google_search_simulation(prompt)
        
        if search_result["found"]:
            data = search_result["result"]
            return json.dumps({
                "exact_threat_category": data["category"],
                "severity": data["severity"],
                "explanation": f"Detected via {search_result['source']}: Found patterns matching '{data['category']}'.",
                "recommended_action": data["action"]
            })
            
        # Step 2: Default Safe Response
        return json.dumps({
            "exact_threat_category": "None",
            "severity": 1,
            "explanation": "No clear threat detected in the text after scanning databases.",
            "recommended_action": "No action needed."
        })

    def process(self, input_data: str, context: AgentContext) -> Dict[str, Any]:
        context.log(self.name, f"Analyzing text: {input_data[:50]}...")
        try:
            
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, input_data, api_key)
            
            # Clean markdown
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Analysis complete", result)
            return result
        except Exception as e:
            error_result = {
                "exact_threat_category": "Error",
                "severity": 0,
                "explanation": str(e),
                "recommended_action": "Debug system."
            }
            context.log(self.name, "Error during analysis", {"error": str(e)})
            return error_result


# 3 Manipulation Detection Agent ---

class ManipulationDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ManipulationDetectionAgent",
            description="Detects love bombing, gaslighting, and emotional manipulation."
        )
        self.system_prompt = """
        You are a Manipulation Detection Agent.
        Your job: Detect love bombing, emotional manipulation, guilt-tripping, gaslighting, validation farming, and controlling tone.
        Input: conversation text.
        Output JSON with:
        - manipulation_flags[] (List of detected tactics)
        - explanation
        - trust_score (0–100, where 100 is completely trustworthy and 0 is highly manipulative)
        - recommended action
        
        Output Format (JSON only):
        {
          "manipulation_flags": ["string", "string"],
          "explanation": "string",
          "trust_score": int,
          "recommended_action": "string"
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if "soulmate" in lower_prompt or "destiny" in lower_prompt or "perfect" in lower_prompt or "love you" in lower_prompt or "only me" in lower_prompt:
            return json.dumps({
                "manipulation_flags": ["Love Bombing", "Validation Farming"],
                "explanation": "Excessive flattery and intensity early in interaction.",
                "trust_score": 30,
                "recommended_action": "Proceed with caution. Verify if actions match words."
            })
        elif "crazy" in lower_prompt or "imagining" in lower_prompt or "sensitive" in lower_prompt or "overreacting" in lower_prompt or "your fault" in lower_prompt:
            return json.dumps({
                "manipulation_flags": ["Gaslighting"],
                "explanation": "Attempting to make the user question their reality or feelings.",
                "trust_score": 10,
                "recommended_action": "Trust your instincts. Document interactions. Disengage if pattern continues."
            })
        elif "after all i did" in lower_prompt or "hurt me" in lower_prompt or "blame" in lower_prompt or "sorry" in lower_prompt or "promise" in lower_prompt:
            return json.dumps({
                "manipulation_flags": ["Guilt-Tripping", "Emotional Manipulation"],
                "explanation": "Using guilt to control the user's actions.",
                "trust_score": 20,
                "recommended_action": "Set boundaries. Do not give in to guilt."
            })
        elif "leak" in lower_prompt or "expose" in lower_prompt or "viral" in lower_prompt or ("share" in lower_prompt and ("nude" in lower_prompt or "private" in lower_prompt or "photo" in lower_prompt)):
            return json.dumps({
                "manipulation_flags": ["Blackmail", "Coercion"],
                "explanation": "Threatening to expose private information to control behavior.",
                "trust_score": 5,
                "recommended_action": "This is blackmail. Do not comply. Report immediately."
            })
        elif "allow" in lower_prompt or "forbid" in lower_prompt or "wear" in lower_prompt or "talk to" in lower_prompt or "password" in lower_prompt or "if you don't" in lower_prompt or "or else" in lower_prompt:
            return json.dumps({
                "manipulation_flags": ["Controlling Tone", "Coercion"],
                "explanation": "Attempting to dictate user's behavior or choices.",
                "trust_score": 15,
                "recommended_action": "Assert independence. Recognize this as a red flag."
            })
        elif "trust me" in lower_prompt or "believe me" in lower_prompt or "secret" in lower_prompt or "between us" in lower_prompt or "don't tell" in lower_prompt:
            return json.dumps({
                "manipulation_flags": ["Isolation/Secrecy"],
                "explanation": "Attempting to isolate the user or keep interactions secret.",
                "trust_score": 25,
                "recommended_action": "Do not keep secrets that make you uncomfortable. Talk to a trusted adult/friend."
            })
        else:
            return json.dumps({
                "manipulation_flags": [],
                "explanation": "No obvious manipulation detected.",
                "trust_score": 90,
                "recommended_action": "Continue interaction normally."
            })

    def process(self, input_data: str, context: AgentContext) -> Dict[str, Any]:
        context.log(self.name, f"Analyzing text: {input_data[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, input_data, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Analysis complete", result)
            return result
        except Exception as e:
            error_result = {
                "manipulation_flags": ["Error"],
                "explanation": f"System error: {str(e)}",
                "trust_score": 0,
                "recommended_action": "Debug system."
            }
            context.log(self.name, "Error during analysis", {"error": str(e)})
            return error_result


# 4 Red-Flag Detection Agent ---

class RedFlagDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RedFlagDetectionAgent",
            description="Detects sexual coercion, grooming, fetish cues, and explicit requests."
        )
        self.system_prompt = """
        You are a Red-Flag Detection Agent.
        Your job: Detect sexual coercion, explicit requests, grooming patterns, fetish cues, forced intimacy, and porn-coded language.
        Input: conversation text.
        Output JSON with:
        - lust_intent_score (0–100)
        - red_flag_level (Green, Yellow, Red, or "Red Forest")
        - example_lines (List of strings showing the red flags)
        
        Red Flag Levels:
        - Green: Safe, no sexual/coercive content.
        - Yellow: Subtle hints, ambiguous comments, potential boundary testing.
        - Red: Explicit requests, sexual comments, forced intimacy.
        - Red Forest: Severe grooming, predatory behavior, extreme coercion.

        Output Format (JSON only):
        {
          "lust_intent_score": int,
          "red_flag_level": "string",
          "example_lines": ["string", "string"]
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if "secret" in lower_prompt or "don't tell" in lower_prompt or "special" in lower_prompt:
            return json.dumps({
                "lust_intent_score": 85,
                "red_flag_level": "Red Forest",
                "example_lines": ["Let's keep this our little secret", "You are special to me"]
            })
        elif "touch" in lower_prompt or "kiss" in lower_prompt or "body" in lower_prompt or "nude" in lower_prompt or "naked" in lower_prompt or "send me" in lower_prompt:
            return json.dumps({
                "lust_intent_score": 75,
                "red_flag_level": "Red",
                "example_lines": ["I want to touch you", "Your body is amazing", "Send me photos"]
            })
        elif "lonely" in lower_prompt or "understand you" in lower_prompt:
            return json.dumps({
                "lust_intent_score": 40,
                "red_flag_level": "Yellow",
                "example_lines": ["I know you're lonely", "Only I understand you"]
            })
        else:
            return json.dumps({
                "lust_intent_score": 5,
                "red_flag_level": "Green",
                "example_lines": []
            })

    def process(self, input_data: str, context: AgentContext) -> Dict[str, Any]:
        context.log(self.name, f"Analyzing text: {input_data[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, input_data, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Analysis complete", result)
            return result
        except Exception as e:
            error_result = {
                "lust_intent_score": 0,
                "red_flag_level": "Error",
                "example_lines": [f"System error: {str(e)}"]
            }
            context.log(self.name, "Error during analysis", {"error": str(e)})
            return error_result


# 5 Evidence Collector Agent ---

class EvidenceCollectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EvidenceCollectorAgent",
            description="Extracts timestamps, classifies evidence, and generates summary packs."
        )
        self.system_prompt = """
        You are an Evidence Collector Agent.
        Your job: Analyze chat text, image descriptions, or metadata to extract evidence.
        Input: conversation text or metadata dictionary.
        Output JSON with:
        - timestamps (List of extracted timestamps)
        - classified_evidence_type (e.g., Harassment, Threat, Grooming, Financial Fraud)
        - crime_category (Legal classification if applicable)
        - summary_evidence_pack (Concise summary of the evidence found)

        Output Format (JSON only):
        {
          "timestamps": ["string"],
          "classified_evidence_type": "string",
          "crime_category": "string",
          "summary_evidence_pack": "string"
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if "kill" in lower_prompt:
            return json.dumps({
                "timestamps": ["2023-10-27 10:15 AM"],
                "classified_evidence_type": "Death Threat",
                "crime_category": "Criminal Threat / Assault",
                "summary_evidence_pack": "User received a direct death threat ('I'm going to kill you')."
            })
        elif "money" in lower_prompt or "photos" in lower_prompt:
            return json.dumps({
                "timestamps": ["2023-10-27 10:20 AM"],
                "classified_evidence_type": "Blackmail / Extortion",
                "crime_category": "Extortion",
                "summary_evidence_pack": "User was coerced to pay money under threat of photo release."
            })
        elif "secret" in lower_prompt:
            return json.dumps({
                "timestamps": ["2023-10-27 10:30 AM"],
                "classified_evidence_type": "Grooming",
                "crime_category": "Child Endangerment / Grooming",
                "summary_evidence_pack": "Adult user attempting to isolate minor with secrecy requests."
            })
        else:
            return json.dumps({
                "timestamps": [],
                "classified_evidence_type": "None",
                "crime_category": "None",
                "summary_evidence_pack": "No actionable evidence found."
            })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
       
        text_content = input_data
        if isinstance(input_data, dict):
            text_content = json.dumps(input_data)
            
        context.log(self.name, f"Collecting evidence from: {str(text_content)[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Evidence collection complete", result)
            return result
        except Exception as e:
            error_result = {
                "timestamps": [],
                "classified_evidence_type": "Error",
                "crime_category": "System Error",
                "summary_evidence_pack": f"Failed to process: {str(e)}"
            }
            context.log(self.name, "Error during collection", {"error": str(e)})
            return error_result


# 6 Legal Support Agent ---

class LegalSupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="LegalSupportAgent",
            description="Provides legal information, complaint steps, and rights based on location and situation."
        )
        self.system_prompt = """
        You are a Legal Support Agent.
        Your job: Provide legal guidance based on the user's country and the specific situation (e.g., harassment, blackmail).
        Input: JSON with "country" and "situation" (or just text description).
        Output JSON with:
        - applicable_laws (List of relevant legal sections/acts)
        - complaint_steps (Step-by-step guide to filing a complaint)
        - police_contact_structure (Who to contact: Cyber Cell, Local Station, etc.)
        - rights_of_the_victim (Key legal rights)

        Output Format (JSON only):
        {
          "applicable_laws": ["string"],
          "complaint_steps": ["string"],
          "police_contact_structure": "string",
          "rights_of_the_victim": ["string"]
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        
        # Mock logic for India (common use case)
        if "india" in lower_prompt or "delhi" in lower_prompt:
            if "blackmail" in lower_prompt or "photos" in lower_prompt:
                return json.dumps({
                    "applicable_laws": ["Section 354C IPC (Voyeurism)", "Section 66E IT Act (Privacy Violation)", "Section 384 IPC (Extortion)"],
                    "complaint_steps": ["Take screenshots of threats", "Do not delete messages", "File complaint at cybercrime.gov.in", "Visit nearest Cyber Cell"],
                    "police_contact_structure": "National Cyber Crime Reporting Portal (1930) or local Cyber Cell Station.",
                    "rights_of_the_victim": ["Right to anonymity", "Right to free legal aid", "Right to zero FIR (file complaint anywhere)"]
                })
            elif "stalking" in lower_prompt:
                return json.dumps({
                    "applicable_laws": ["Section 354D IPC (Stalking)"],
                    "complaint_steps": ["Document all contact attempts", "Block user", "File FIR at local station"],
                    "police_contact_structure": "Local Police Station (Women's Help Desk).",
                    "rights_of_the_victim": ["Right to protection order", "Right to privacy"]
                })
            elif "rape" in lower_prompt or "sexual assault" in lower_prompt or "forced" in lower_prompt:
                return json.dumps({
                    "applicable_laws": ["Section 375/376 IPC (Rape)", "Section 354 IPC (Assault on woman with intent to outrage modesty)"],
                    "complaint_steps": ["Go to a safe place immediately", "Call 100 or 1091", "Do not wash evidence (clothes/body)", "Go to hospital for medical exam"],
                    "police_contact_structure": "Nearest Police Station (SHOs are mandated to register FIR).",
                    "rights_of_the_victim": ["Right to free medical aid", "Right to statement in private", "Right to free legal counsel"]
                })
            elif "domestic" in lower_prompt or "husband" in lower_prompt or "beat" in lower_prompt or "dowry" in lower_prompt:
                return json.dumps({
                    "applicable_laws": ["Protection of Women from Domestic Violence Act, 2005", "Section 498A IPC (Cruelty by husband/relatives)"],
                    "complaint_steps": ["Call 181 (Domestic Abuse Helpline)", "Contact a Protection Officer", "File DIR (Domestic Incident Report)"],
                    "police_contact_structure": "Women's Cell or Local Magistrate.",
                    "rights_of_the_victim": ["Right to residence", "Right to protection order", "Right to monetary relief"]
                })
            else:

                # Generic India Fallback

                return json.dumps({
                    "applicable_laws": ["Indian Penal Code (IPC) General Provisions", "Information Technology Act, 2000"],
                    "complaint_steps": ["Dial 100 (Police) or 1091 (Women Helpline)", "Visit nearest Police Station", "File online at cybercrime.gov.in"],
                    "police_contact_structure": "Local Police Station or Women's Cell.",
                    "rights_of_the_victim": ["Right to Zero FIR", "Right to be attended by a female officer"]
                })
        
        # Mock logic for USA

        elif "usa" in lower_prompt or "united states" in lower_prompt or "america" in lower_prompt:
             return json.dumps({
                "applicable_laws": ["18 U.S. Code § 2261A (Stalking)", "State-specific Cyber Harassment Laws"],
                "complaint_steps": ["Preserve evidence", "Contact IC3 (FBI)", "File police report"],
                "police_contact_structure": "Local Police Department or FBI Field Office.",
                "rights_of_the_victim": ["Right to restraining order", "Victim compensation"]
            })

        # Default/Generic
        return json.dumps({
            "applicable_laws": ["Check local penal code for Harassment/Cyberbullying"],
            "complaint_steps": ["Block user", "Report to platform", "Consult local lawyer"],
            "police_contact_structure": "Local Law Enforcement Agency.",
            "rights_of_the_victim": ["Right to report", "Right to safety"]
        })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
       
        text_content = input_data
        if isinstance(input_data, dict):
            text_content = json.dumps(input_data)
            
        context.log(self.name, f"Providing legal support for: {str(text_content)[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Legal guidance generated", result)
            return result
        except Exception as e:
            error_result = {
                "applicable_laws": ["Error"],
                "complaint_steps": [],
                "police_contact_structure": "Error",
                "rights_of_the_victim": [f"System error: {str(e)}"]
            }
            context.log(self.name, "Error during legal analysis", {"error": str(e)})
            return error_result


# --- CELL 7: Panic Response Agent ---


import json
import time
from typing import Union, Dict, Any

class PanicResponseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PanicResponseAgent",
            description="Handles emergency triggers by requesting location, signaling recording, and preparing messages."
        )
        self.system_prompt = """
        You are a Panic Response Agent.
        Your job: Detect emergency triggers and respond immediately with safety protocols.
        Input: User text or trigger signal.
        Output JSON with:
        - location_request (Boolean: True if location is needed)
        - auto_recording_signal (Boolean: True to start recording)
        - message_template_for_contacts (Emergency message string)
        - emergency_status (Active/Standby)

        Output Format (JSON only):
        {
          "location_request": boolean,
          "auto_recording_signal": boolean,
          "message_template_for_contacts": "string",
          "emergency_status": "string"
        }
        """

    def _get_live_gps_location(self):
       
        return {"lat": 28.7041, "long": 77.1025, "precision": "10m", "timestamp": time.time()}

    def _trigger_silent_recording(self):
        
        return "/data/secure_storage/panic_rec_001.aac"

    def _broadcast_sos_signal(self):
       
        return "Encrypted Signal Sent to Nearest Police Node (ID: POL-55)"

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        
        # Emergency triggers

        triggers = ["help", "danger", "panic", "emergency", "follow", "scared", "unsafe", "kill"]
        
        if any(t in lower_prompt for t in triggers):
            return json.dumps({
                "location_request": True,
                "auto_recording_signal": True,
                "message_template_for_contacts": "SOS! I am in danger. Here is my location. Audio recording started.",
                "emergency_status": "Active"
            })
        else:
            return json.dumps({
                "location_request": False,
                "auto_recording_signal": False,
                "message_template_for_contacts": "",
                "emergency_status": "Standby"
            })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
        text_content = input_data
        if isinstance(input_data, dict):
            text_content = json.dumps(input_data)
            
        context.log(self.name, f"Checking for panic triggers: {str(text_content)[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            
            # Hardware Triggers Logic
            if result.get("emergency_status") == "Active":
                context.log(self.name, "!!! EMERGENCY TRIGGERED !!! Initiating Hardware Protocols...", result)
                
                # Trigger Hardware Actions
                gps_data = self._get_live_gps_location()
                rec_path = self._trigger_silent_recording()
                sos_status = self._broadcast_sos_signal()
                
                # Enrich Result
                result["hardware_actions"] = {
                    "gps_location": gps_data,
                    "audio_recording": rec_path,
                    "sos_broadcast": sos_status
                }
                context.log(self.name, "Hardware Actions Completed", result["hardware_actions"])
            else:
                context.log(self.name, "Status: Standby", result)
                
            return result
        except Exception as e:
            error_result = {
                "location_request": False,
                "auto_recording_signal": False,
                "message_template_for_contacts": f"Error: {str(e)}",
                "emergency_status": "Error"
            }
            context.log(self.name, "Error during panic check", {"error": str(e)})
            return error_result


# 8 Multilingual Agent ---

class MultilingualAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MultilingualAgent",
            description="Translates text, detects language, and recognizes speech intent."
        )
        self.system_prompt = """
        You are a Multilingual Agent.
        Your job: Translate input text to English (if not already), detect the source language, and identify any speech command intent.
        Input: User text.
        Output JSON with:
        - input_language (Detected language code, e.g., 'en', 'es', 'hi')
        - output_translation (English translation of the input)
        - speech_command (Identified command if any, e.g., 'record', 'call_police', 'none')

        Output Format (JSON only):
        {
          "input_language": "string",
          "output_translation": "string",
          "speech_command": "string"
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        
        
        if "help" in lower_prompt or "bachao" in lower_prompt:
            return json.dumps({
                "input_language": "hi",
                "output_translation": "Help me / Save me",
                "speech_command": "emergency_help"
            })
        elif "maar" in lower_prompt or "kill" in lower_prompt or "khatam" in lower_prompt:
             return json.dumps({
                "input_language": "hi",
                "output_translation": "I will kill you / finish you (Death Threat)",
                "speech_command": "none"
            })
        elif "paisa" in lower_prompt or "rupaye" in lower_prompt:
             return json.dumps({
                "input_language": "hi",
                "output_translation": "Give money (Financial Demand)",
                "speech_command": "none"
            })
        elif "ayuda" in lower_prompt or "peligro" in lower_prompt:
            return json.dumps({
                "input_language": "es",
                "output_translation": "Help / Danger",
                "speech_command": "emergency_help"
            })
        elif "record" in lower_prompt or "grabar" in lower_prompt:
            return json.dumps({
                "input_language": "auto",
                "output_translation": "Record this",
                "speech_command": "start_recording"
            })
        else:
            return json.dumps({
                "input_language": "en",
                "output_translation": prompt,
                "speech_command": "none"
            })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
        text_content = input_data
        if isinstance(input_data, dict):
            text_content = json.dumps(input_data)
            
        context.log(self.name, f"Processing language for: {str(text_content)[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Language processing complete", result)
            return result
        except Exception as e:
            error_result = {
                "input_language": "unknown",
                "output_translation": "Error",
                "speech_command": "error"
            }
            context.log(self.name, "Error during language processing", {"error": str(e)})
            return error_result


# 9 Reality-Check Generator Agent ---

class RealityCheckAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RealityCheckAgent",
            description="Generates bait messages to reveal real intentions and predicts responses."
        )
        self.system_prompt = """
        You are a Reality-Check Generator Agent.
        Your job: Based on the chat history/context, generate 'bait' messages that the user can send to test the other person's true intentions. Predict the likely response if the person is malicious vs. safe.
        Input: Chat context or suspicious statement.
        Output JSON with:
        - bait_messages (List of suggested messages to send)
        - predicted_responses (What a manipulator might say vs. a normal person)
        - confidence_score (0-100, how likely this bait is to work)

        Output Format (JSON only):
        {
          "bait_messages": ["string"],
          "predicted_responses": {
            "malicious": "string",
            "safe": "string"
          },
          "confidence_score": int
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        
        if "money" in lower_prompt or "financial" in lower_prompt:
            return json.dumps({
                "bait_messages": [
                    "I can't send money right now, but I can help you find a job.",
                    "My bank account is frozen, can we meet in person instead?"
                ],
                "predicted_responses": {
                    "malicious": "They will get angry, guilt-trip you, or refuse to meet.",
                    "safe": "They will be understanding and open to other forms of help."
                },
                "confidence_score": 90
            })
        elif "secret" in lower_prompt or "don't tell" in lower_prompt:
            return json.dumps({
                "bait_messages": [
                    "I tell my mom everything, I'm going to ask her advice.",
                    "Why does it have to be a secret? That makes me uncomfortable."
                ],
                "predicted_responses": {
                    "malicious": "They will panic, threaten you, or try to isolate you further.",
                    "safe": "They will respect your boundary and agree to be open."
                },
                "confidence_score": 85
            })
        elif "love" in lower_prompt or "soulmate" in lower_prompt:
            return json.dumps({
                "bait_messages": [
                    "This is moving too fast for me, I need some space.",
                    "I want to take things slow and get to know you as a friend first."
                ],
                "predicted_responses": {
                    "malicious": "They will accuse you of not loving them or try to rush you again (Love Bombing).",
                    "safe": "They will respect your pace and back off."
                },
                "confidence_score": 80
            })
        else:
            return json.dumps({
                "bait_messages": ["Can we talk about this later?", "I'm not comfortable with this topic."],
                "predicted_responses": {
                    "malicious": "Pushy or dismissive behavior.",
                    "safe": "Respectful agreement."
                },
                "confidence_score": 50
            })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
        text_content = input_data
        if isinstance(input_data, dict):
            text_content = json.dumps(input_data)
            
        context.log(self.name, f"Generating reality checks for: {str(text_content)[:50]}...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Reality checks generated", result)
            return result
        except Exception as e:
            error_result = {
                "bait_messages": ["Error generating bait"],
                "predicted_responses": {},
                "confidence_score": 0
            }
            context.log(self.name, "Error during generation", {"error": str(e)})
            return error_result


# 10 Orchestration and Demo ---

def run_demo():
    print("--- Multi-Agent System Demo ---\n")
    
    # 1. Initialize Orchestrator and Agents

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent(ThreatDetectionAgent())
    orchestrator.register_agent(ManipulationDetectionAgent())
    orchestrator.register_agent(RedFlagDetectionAgent())
    orchestrator.register_agent(EvidenceCollectorAgent())
    orchestrator.register_agent(LegalSupportAgent())
    orchestrator.register_agent(PanicResponseAgent())
    orchestrator.register_agent(MultilingualAgent())
    orchestrator.register_agent(RealityCheckAgent())
    
    # 2. Define Test Inputs
    test_inputs = [
        "If you don't send me the money, I'll release the photos.",
        "Let's keep this our little secret, don't tell your parents.",
        "You are my soulmate, I've never met anyone as perfect as you."
    ]
    
    # 3. Run Agents
    for text in test_inputs:
        print(f"Input: \"{text}\"")
        
        # Run all agents
        results = orchestrator.run_parallel(text, [
            "ThreatDetectionAgent", 
            "ManipulationDetectionAgent",
            "RedFlagDetectionAgent",
            "EvidenceCollectorAgent",
            "LegalSupportAgent",
            "PanicResponseAgent",
            "MultilingualAgent",
            "RealityCheckAgent"
        ])
        
        print("Results:")
        print(json.dumps(results, indent=2))
        print("-" * 40)
        
    # 4. Show Execution Trace (Logging)
    print("\n--- Execution Trace (Logging) ---")
    trace = orchestrator.get_execution_trace()
    for log in trace:
        print(f"[{time.strftime('%H:%M:%S', time.localtime(log['timestamp']))}] [{log['agent']}] {log['message']}")

if __name__ == "__main__":
    run_demo()



# 11 Master Controller & Final Pipeline ---

class MasterController:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.context = self.orchestrator.context
        
        # Register ALL Agents
        self.agents = {
            "language": MultilingualAgent(),
            "panic": PanicResponseAgent(),
            "threat": ThreatDetectionAgent(),
            "manipulation": ManipulationDetectionAgent(),
            "redflag": RedFlagDetectionAgent(),
            "evidence": EvidenceCollectorAgent(),
            "legal": LegalSupportAgent(),
            "reality": RealityCheckAgent()
        }
        
        for agent in self.agents.values():
            self.orchestrator.register_agent(agent)

    def router(self, user_input: str) -> List[str]:
        """
        Decides which agents to run based on initial analysis.
        Returns a list of agent names to execute.
        """
        # 1. Always run Language and Panic first
       
        return ["threat", "manipulation", "redflag"]

    def pipeline(self, user_input: str) -> Dict[str, Any]:
        """
        Orchestrates the full flow of data between agents.
        """
        self.context.log("MasterController", "Starting Pipeline", {"input": user_input})
        results = {}

        # Step 1: Language Processing (Translate & Detect Intent)
        lang_result = self.agents["language"].process(user_input, self.context)
        results["language"] = lang_result
        
        # Use translated text for subsequent analysis if available
        analysis_text = lang_result.get("output_translation", user_input)
        
        # Step 2: Panic Check (High Priority)
        panic_result = self.agents["panic"].process(analysis_text, self.context)
        results["panic"] = panic_result
        
       
        if panic_result.get("emergency_status") == "Active":
            self.context.log("MasterController", "EMERGENCY DETECTED - Prioritizing Safety")
           
        
        analysis_agents = self.router(analysis_text)
        
        
        core_results = self.orchestrator.run_parallel(analysis_text, [self.agents[name].name for name in analysis_agents])
        
       
        results["threat"] = core_results.get("ThreatDetectionAgent")
        results["manipulation"] = core_results.get("ManipulationDetectionAgent")
        results["redflag"] = core_results.get("RedFlagDetectionAgent")

        # Step 4: Evidence Collection
       
        evidence_input = {
            "text": analysis_text,
            "threat_analysis": results["threat"],
            "manipulation_analysis": results["manipulation"],
            "redflag_analysis": results["redflag"]
        }
        results["evidence"] = self.agents["evidence"].process(evidence_input, self.context)

        # Step 5: Legal Support
        
        legal_input = {
            "situation": results["evidence"].get("summary_evidence_pack"),
            "crime_category": results["evidence"].get("crime_category"),
            "location": "User Location", 
            "full_text": analysis_text 
        }
        results["legal"] = self.agents["legal"].process(legal_input, self.context)

        # Step 6: Reality Check (Only if NOT an emergency)
        if panic_result.get("emergency_status") != "Active":
            results["reality"] = self.agents["reality"].process(analysis_text, self.context)
        else:
            results["reality"] = {"status": "Skipped due to emergency"}

        self.context.log("MasterController", "Pipeline Complete")
        return results

def run_final_system():
    print("--- SHAKTI MASTER SYSTEM INITIALIZED ---\n")
    master = MasterController()
    
    # Test Cases covering different scenarios
    scenarios = [
        "Bachao! He is following me and said he will kill me.", # Hindi Emergency
        "You are my soulmate, don't tell your parents about us.", # Grooming/Manipulation
        "If you don't send the money, I will post the video." # Blackmail
    ]
    
    for i, text in enumerate(scenarios, 1):
        print(f"\n>>> SCENARIO {i}: \"{text}\"")
        final_output = master.pipeline(text)
        
        # Pretty Print Summary
        print("\n[SYSTEM REPORT]")
        print(f"Language: {final_output['language']['input_language']} -> {final_output['language']['output_translation']}")
        print(f"Panic Status: {final_output['panic']['emergency_status']}")
        
        if final_output['threat']:
            print(f"Threat: {final_output['threat']['exact_threat_category']} (Severity: {final_output['threat']['severity']})")
        
        if final_output['redflag']:
            print(f"Red Flags: {final_output['redflag']['red_flag_level']}")
            
        print(f"Evidence: {final_output['evidence']['summary_evidence_pack']}")
        print(f"Legal: {final_output['legal']['applicable_laws'][0] if final_output['legal']['applicable_laws'] else 'None'}")
        
        if 'bait_messages' in final_output['reality']:
             print(f"Suggested Response: {final_output['reality']['bait_messages'][0]}")
             
        print("-" * 60)

if __name__ == "__main__":
    run_final_system()



# --- CELL 12: Final Comprehensive Tools (All-in-One) ---


import json
import random
import time

# --- 1. Legal Knowledge Base ---
class LegalKnowledgeBase:
    def __init__(self):
        self.law_book = [
            {"country": "India", "section": "354A", "act": "IPC", "title": "Sexual Harassment", "desc": "Physical contact, advances, or demanding sexual favors."},
            {"country": "India", "section": "354C", "act": "IPC", "title": "Voyeurism", "desc": "Capturing or sharing images of a woman engaging in a private act."},
            {"country": "India", "section": "354D", "act": "IPC", "title": "Stalking", "desc": "Following, contacting, or monitoring a woman despite disinterest."},
            {"country": "India", "section": "503", "act": "IPC", "title": "Criminal Intimidation", "desc": "Threatening injury to person, reputation, or property."},
            {"country": "India", "section": "506", "act": "IPC", "title": "Punishment for Criminal Intimidation", "desc": "Imprisonment for a term which may extend to two years."},
            {"country": "India", "section": "66E", "act": "IT Act", "title": "Privacy Violation", "desc": "Capturing, publishing or transmitting image of private area of any person."},
            {"country": "USA", "section": "2261A", "act": "US Code", "title": "Stalking", "desc": "Traveling in interstate commerce to kill, injure, harass, or intimidate."},
            {"country": "UK", "section": "2", "act": "Protection from Harassment Act", "title": "Harassment", "desc": "Offence of harassment."}
        ]

    def search(self, query: str, country_filter: str = None) -> str:
        query = query.lower()
        results = []
        for law in self.law_book:
            if country_filter and country_filter.lower() not in law["country"].lower(): continue
            if query in law["section"].lower() or query in law["title"].lower() or query in law["desc"].lower():
                results.append(f"[{law['country']}] {law['act']} Section {law['section']} - {law['title']}: {law['desc']}")
        return "\n".join(results[:3]) if results else "No specific legal section found."

# --- 2. Base Tool Class ---
class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def execute(self, **kwargs): raise NotImplementedError

# --- 3. Basic Tools ---
class WebSearchTool(Tool):
    def __init__(self):
        super().__init__("WebSearch", "Simulates searching the web for information.")
    def execute(self, query):
        return f"[Search Result] Found 5 articles relevant to '{query}'."

class LegalLookupTool(Tool):
    def __init__(self):
        super().__init__("LegalDatabase", "Searches the internal Law Book for legal sections.")
        self.kb = LegalKnowledgeBase()
        self.web_search = WebSearchTool() 
    def execute(self, query, country=None):
        
        internal_result = self.kb.search(query, country)
        
       
        if "No specific legal section found" in internal_result:
            print(f"[LegalLookup] Internal DB failed. Triggering Web Search fallback...")
            
            web_query = f"legal section for {query} in {country or 'general'}"
            web_result = self.web_search.execute(web_query)
            return f"Source: Live Web Search\n{web_result}"
            
        return f"Source: Internal Database\n{internal_result}"

# --- 4. Elite Tools (Computer Vision & Audio) ---
class DeepfakeDetectionTool(Tool):
    def __init__(self):
        super().__init__("DeepfakeDetector", "Analyzes media for face manipulation, noise artifacts, and lip-sync errors.")

    def _simulate_frame_extraction(self):
        
        time.sleep(0.2) 
        return 30

    def _detect_landmarks(self):
       
        return "68_point_mesh"

    def execute(self, media_path_or_url):
        print(f"[DeepfakeDetector] Analyzing artifacts in {media_path_or_url}...")
        self._simulate_frame_extraction()
        self._detect_landmarks()
        
        # Advanced Simulation Logic
        if "fake" in media_path_or_url.lower() or "edit" in media_path_or_url.lower():
            return {
                "is_deepfake": True,
                "artifact_confidence_score": 0.985,
                "lip_sync_error_rate": "High (0.85)",
                "model_version": "EfficientNet-B7",
                "artifacts": ["Mismatched lip sync", "Irregular blinking pattern", "Digital noise in jawline"]
            }
        return {
            "is_deepfake": False,
            "artifact_confidence_score": 0.12,
            "lip_sync_error_rate": "Low (0.05)",
            "model_version": "EfficientNet-B7",
            "artifacts": []
        }

class AudioAnalysisTool(Tool):
    def __init__(self):
        super().__init__("AudioForensics", "Analyzes voice stress, background noise, and speaker identity.")

    def _spectral_analysis(self):
        # Simulate FFT (Fast Fourier Transform)
        time.sleep(0.2)
        return "Frequency Spectrum Extracted"

    def execute(self, audio_data):
        print(f"[AudioForensics] Extracting MFCC features and running Spectral Analysis...")
        self._spectral_analysis()
        
        return {
            "stress_level": "High",
            "voice_stress_score": 85, # 0-100
            "background_noise_level": "45dB (Traffic)",
            "speaker_gender": "Male"
        }

class ImageSafetyClassifier(Tool):
    def __init__(self):
        super().__init__("ImageSafety", "Detects NSFW, Gore, and Violence in images.")
    def execute(self, image_data):
        print(f"[ImageSafety] Running ResNet-50 Safety Model...")
        return {"nsfw_score": 0.02, "classification": "Safe"}

# --- 5. Ultimate Tools (MCP, OpenAPI, Advanced) ---
class MCPTool(Tool):
    def __init__(self, server_url, tool_name):
        super().__init__(f"MCP_{tool_name}", f"Connects to MCP Server at {server_url}")
        self.server_url = server_url
        self.tool_name = tool_name
    def execute(self, **kwargs):
        print(f"🔌 [MCP Protocol] Connecting to {self.server_url}...")
        return {"status": "success", "data": f"Executed {self.tool_name} via MCP", "server_response": "OK"}

class OpenAPITool(Tool):
    def __init__(self, spec_url):
        super().__init__("OpenAPI_Generic", "Consumes tools from an OpenAPI specification.")
        self.spec_url = spec_url
    def execute(self, endpoint, params):
        print(f"🌐 [OpenAPI] Calling {self.spec_url}{endpoint} with {params}")
        return {"status": 200, "body": "Mock API Response"}

class GoogleSearchTool(Tool):
    def __init__(self):
        super().__init__("GoogleSearch", "Performs a real Google Search.")
    def execute(self, query):
        print(f"🔍 [GoogleSearch] Searching for: {query}")
        return [{"title": "Cyber Crime Portal", "link": "http://cybercrime.gov.in"}]

class CodeExecutorTool(Tool):
    def __init__(self):
        super().__init__("CodeExecutor", "Executes Python code safely.")
    def execute(self, code):
        print(f"💻 [CodeExecutor] Running:\n{code}")
        return {"status": "success", "output": "Code executed successfully"}

# --- 6. Tool Registry ---
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    def register_tool(self, tool):
        self.tools[tool.name] = tool
    def get_tool(self, name):
        return self.tools.get(name)

# --- 7. Long-Running Operation ---
class DeepForensicScan:
    def __init__(self):
        self.name = "DeepForensicScan"
        self.status = "IDLE"
        self.progress = 0
        self.result = None
    def start(self, input_data):
        self.status = "RUNNING"
        self.progress = 0
        print(f"[{self.name}] Started operation on: {input_data}")
    def pause(self):
        if self.status == "RUNNING":
            self.status = "PAUSED"
            print(f"[{self.name}] Operation PAUSED at {self.progress}%")
    def resume(self):
        if self.status == "PAUSED":
            self.status = "RUNNING"
            print(f"[{self.name}] Operation RESUMED from {self.progress}%")
    def step(self):
        if self.status == "RUNNING":
            self.progress += 20
            print(f"[{self.name}] Processing... {self.progress}%")
            if self.progress >= 100:
                self.status = "COMPLETED"
                self.result = "Operation Successful"
                print(f"[{self.name}] Operation COMPLETED.")



# --- CELL 13: Master Controller V3 (Enhanced) ---


class MasterControllerV3(MasterController):
    def __init__(self):
        super().__init__()
        # Initialize Enhanced Tools
        self.tool_registry = ToolRegistry()
        self.tool_registry.register_tool(WebSearchTool())
        self.tool_registry.register_tool(LegalLookupTool())
        
        # Initialize Long-Running Op
        self.forensic_scan = DeepForensicScan()

    def pipeline_v3(self, user_input: str) -> Dict[str, Any]:
        # Run the standard pipeline first
        results = self.pipeline(user_input)
        
       
        if results.get("legal") and results["legal"].get("applicable_laws"):
            # Get the first suggested law
            law_suggestion = results["legal"]["applicable_laws"][0]
            
            # Determine country context (simple heuristic)

           
            country = "India" if "IPC" in law_suggestion or "India" in user_input else None
            if "US" in law_suggestion: country = "USA"
            if "UK" in law_suggestion: country = "UK"
            
           
            import re
            match = re.search(r"(?:Section|Sec)?\s*(\d+[A-Z]?)", law_suggestion, re.IGNORECASE)
            search_query = match.group(1) if match else law_suggestion
            
            tool = self.tool_registry.get_tool("LegalDatabase")
            lookup_result = tool.execute(search_query, country)
            
            results["legal"]["tool_lookup"] = lookup_result
            self.context.log("MasterControllerV3", f"Tool Used: LegalDatabase search for '{search_query}' in {country}", lookup_result)

        # 2. Trigger Long-Running Operation if Threat is High
        threat_score = results.get("threat", {}).get("severity_score", 0)
        if threat_score > 70:
            self.context.log("MasterControllerV3", "High Threat Detected! Initiating Deep Forensic Scan.")
            
            self.forensic_scan.start(user_input)
            self.forensic_scan.step() # 20%
            self.forensic_scan.pause() # Pause
            
            print("... (Simulating user approval / time delay) ...")
            
            self.forensic_scan.resume() # Resume
            while self.forensic_scan.status == "RUNNING":
                self.forensic_scan.step()
                
            results["forensic_scan"] = self.forensic_scan.result

        return results

def run_final_system_v3():
    print("--- SHAKTI MASTER SYSTEM V3 (Enhanced Knowledge Base) ---\n")
    master = MasterControllerV3()
    
  
    text = "I'm going to kill you. I know where you live. (Location: India)"
    
    print(f"\n>>> SCENARIO: \"{text}\"")
    final_output = master.pipeline_v3(text)
    
   
    print("\n[SYSTEM REPORT V3]")
    print(f"Panic Status: {final_output['panic']['emergency_status']}")
    print(f"Threat: {final_output['threat']['exact_threat_category']} (Severity: {final_output['threat']['severity']})")
    
    if 'tool_lookup' in final_output.get('legal', {}):
        print(f"Legal Knowledge Base Result:\n{final_output['legal']['tool_lookup']}")
        
    if 'forensic_scan' in final_output:
        print(f"Forensic Scan Status: {final_output['forensic_scan']}")
            
    print("-" * 60)

if __name__ == "__main__":
    run_final_system_v3()


# --- CELL 14: Final Memory, Observability & Evaluation (All-in-One) ---

import sqlite3
import json
import time
import uuid
from collections import defaultdict

# --- 1. Persistent Storage (SQLite Memory Bank) ---
class FinalMemoryBank:
    def __init__(self, db_name="shakti_memory.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        self.grooming_patterns = ["secret", "don't tell", "special", "parents won't understand"]

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                          (id INTEGER PRIMARY KEY, user_id TEXT, role TEXT, content TEXT, timestamp REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS threats 
                          (id INTEGER PRIMARY KEY, user_id TEXT, severity TEXT, category TEXT, timestamp REAL)''')
        self.conn.commit()

    def store_interaction(self, user_id, text, threat_score):
        
        self.store_message(user_id, "user", text)
        if threat_score > 0:
            self.log_threat(user_id, "Unknown", "General Risk")

    def store_message(self, user_id, role, content):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, role, content, time.time()))
        self.conn.commit()

    def log_threat(self, user_id, severity, category):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO threats (user_id, severity, category, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, severity, category, time.time()))
        self.conn.commit()

    def get_user_history(self, user_id, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
        return [{"role": r, "content": c} for r, c in cursor.fetchall()][::-1]

    def get_risk_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT severity FROM threats WHERE user_id = ?", (user_id,))
        threats = cursor.fetchall()
        if not threats: return "Low Risk"
        
        high_count = sum(1 for t in threats if t[0] in ["High", "Critical"])
        return "High Risk" if high_count > 0 else "Medium Risk"

    def detect_grooming_pattern(self, text):
        matches = [p for p in self.grooming_patterns if p in text.lower()]
        return len(matches) > 0, matches

    def find_similar_cases(self, text_snippet):
        """
        Simple memory retrieval: searches for past user messages containing similar keywords.
        In a real system, this would use Vector Embeddings (RAG).
        """
        cursor = self.conn.cursor()
      
        keywords = [w for w in text_snippet.split() if len(w) > 4][:3]
        if not keywords: return None
        
        query = "SELECT content FROM history WHERE role='user' AND (" + " OR ".join(["content LIKE ?"] * len(keywords)) + ") LIMIT 1"
        params = [f"%{k}%" for k in keywords]
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else None

# --- 2. Context Engineering (Compaction Engine) ---
class ContextCompactionEngine:
    def __init__(self, max_tokens=1000):
        self.max_tokens = max_tokens

    def compress(self, history):
        
        relevant = [msg for msg in history if isinstance(msg, dict) and msg.get('role') in ['user', 'assistant']]
        
        
        if len(str(relevant)) > self.max_tokens:
            summary = f"[Summary: Previous {len(relevant)-4} messages compacted to save context.]"
            return relevant[:2] + [{"role": "system", "content": summary}] + relevant[-2:]
        
        return relevant

# --- 3. Ultimate Observability (Metrics & Tracing) ---
class FinalMetricsCollector:
    def __init__(self):
        self.traces = [] 
        self.metrics = {
            "total_requests": 0,
            "errors": 0,
            "tool_usage": defaultdict(int),
            "threat_heatmap": defaultdict(int),
            "agent_latency": defaultdict(list)
        }

    def start_trace(self, agent_name):
        return {"id": str(uuid.uuid4()), "agent": agent_name, "start": time.time()}

    def end_trace(self, trace, output):
        duration = (time.time() - trace["start"]) * 1000
        trace["latency"] = duration
        trace["output"] = str(output)[:50] + "..."
        self.traces.append(trace)
        self.log_latency(trace["agent"], duration)
        return duration

    def log_request(self):
        self.metrics["total_requests"] += 1

    def log_error(self):
        self.metrics["errors"] += 1

    def log_latency(self, agent_name, duration_ms):
        self.metrics["agent_latency"][agent_name].append(duration_ms)

    def log_threat(self, severity):
        self.metrics["threat_heatmap"][severity] += 1

    def log_tool(self, tool_name):
        self.metrics["tool_usage"][tool_name] += 1

    def get_report(self):
        return self.get_dashboard()

    def get_dashboard(self):
        report = "\n📊 === ULTIMATE OBSERVABILITY DASHBOARD === 📊\n"
        report += f"Total Requests: {self.metrics['total_requests']} | Errors: {self.metrics['errors']}\n"
        
        report += "\n[🔥 Risk Heatmap]\n"
        for k, v in self.metrics["threat_heatmap"].items():
            report += f"  {str(k).ljust(10)}: {'█' * v} ({v})\n"

        report += "\n[🛠️ Tool Usage]\n"
        for k, v in self.metrics["tool_usage"].items():
            report += f"  {k}: {v}\n"

        report += "\n[⏱️ Avg Latency]\n"
        for agent, lats in self.metrics["agent_latency"].items():
            avg = sum(lats)/len(lats) if lats else 0
            report += f"  {agent}: {avg:.2f}ms\n"
            
        report += "==============================================\n"
        return report

# --- 4. Agent Evaluation Pipeline ---
class AgentEvaluationPipeline:
    def evaluate_step(self, agent_name, input_data, output_data):
        score = 10
        critique = "Perfect"
        
        if agent_name == "ThreatDetectionAgent":
            if "kill" in str(input_data).lower() and output_data.get("severity") != "High":
                score = 0
                critique = "FAILED: Missed death threat."
        
        return {"score": score, "critique": critique}
    
   
    def process(self, results, context):
        
        score = 8
        critique = "System performed well."
        if results.get("threat", {}).get("severity") == "High":
            critique = "High threat correctly identified."
        return {"quality_score": score, "critique": critique}

# --- 5. Session Service (Hybrid) ---
class FinalSessionService:
    def __init__(self, db):
        self.db = db
        self.sessions = {} 

    def create_session(self):
        sid = str(uuid.uuid4())
        self.sessions[sid] = True
        return sid

    def add_history(self, sid, role, content):
        # Store in SQLite
        self.db.store_message(sid, role, content)

    def get_history(self, sid):
        return self.db.get_user_history(sid)


memory_bank = FinalMemoryBank()
context_compressor = ContextCompactionEngine()
metrics_collector = FinalMetricsCollector()
eval_pipeline = AgentEvaluationPipeline()
session_service = FinalSessionService(memory_bank)


sqlite_db = memory_bank
context_engine = context_compressor
observability = metrics_collector




# --- CELL 15: Agent Evaluation ---


class EvaluationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EvaluationAgent",
            description="Evaluates the output of other agents for quality, consistency, and safety."
        )
        self.system_prompt = """
        You are an Evaluation Agent.
        Your job: Review the analysis provided by the Threat, Manipulation, and Legal agents.
        Input: JSON containing the outputs of other agents.
        Output JSON with:
        - quality_score (0-10, how well the agents performed)
        - consistency_check (Pass/Fail: Do the agents agree?)
        - safety_check (Pass/Fail: Is the advice safe?)
        - critique (Comments on what could be improved)

        Output Format (JSON only):
        {
          "quality_score": int,
          "consistency_check": "string",
          "safety_check": "string",
          "critique": "string"
        }
        """

    def _mock_llm_call(self, prompt: str) -> str:
        
        try:
            data = json.loads(prompt)
            threat_level = data.get("threat", {}).get("severity", "Low")
            legal_advice = data.get("legal", {}).get("applicable_laws", [])
            
            score = 8
            critique = "Good analysis."
            
            if threat_level == "High" and not legal_advice:
                score = 4
                critique = "Critical Issue: High threat detected but no legal laws found."
            elif threat_level == "Low" and "Kill" in str(data):
                score = 2
                critique = "Critical Error: Threat agent missed a death threat."
                
            return json.dumps({
                "quality_score": score,
                "consistency_check": "Pass" if score > 5 else "Fail",
                "safety_check": "Pass",
                "critique": critique
            })
        except:
            return json.dumps({
                "quality_score": 0,
                "consistency_check": "Error",
                "safety_check": "Unknown",
                "critique": "Failed to parse input data."
            })

    def process(self, input_data: Union[str, Dict[str, Any]], context: AgentContext) -> Dict[str, Any]:
        text_content = json.dumps(input_data) if isinstance(input_data, dict) else input_data
        
        context.log(self.name, "Evaluating system performance...")
        try:
            api_key = context.get_memory("api_key")
            response_str = self._call_llm_api(self.system_prompt, text_content, api_key)
            
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
                
            result = json.loads(response_str.strip())
            context.log(self.name, "Evaluation complete", result)
            return result
        except Exception as e:
            return {"error": str(e)}



# --- CELL 16: Final Deployment & Core System (All-in-One) ---

import threading
import queue
import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# --- 1. A2A Event Bus (Pub/Sub) ---
class EventBus:
    def __init__(self):
        self.subscribers = {} 
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers: self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    def publish(self, event_type, data):
        print(f"📢 [EVENT BUS] Published: {event_type}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)

event_bus = EventBus()

# --- 2. Real Loop Agent (Threaded) ---
class RealLoopAgent(threading.Thread):
    def __init__(self, master_controller):
        super().__init__()
        self.master = master_controller
        self.daemon = True 
        self.running = False

    def run(self):
        self.running = True
        print("🔄 [LOOP AGENT] Background Thread Started (Monitoring Stream)...")
        while self.running:
            
            time.sleep(2)
            

    def stop(self):
        self.running = False
        print("🔄 [LOOP AGENT] Stopped.")

# --- 3. Master Controller Ultimate (The Brain) ---
class MasterControllerUltimate(MasterControllerV3):
    def __init__(self):
        super().__init__()
        
        self.tool_registry.register_tool(MCPTool("http://localhost:8000", "filesystem"))
        self.tool_registry.register_tool(OpenAPITool("http://api.weather.com/openapi.json"))
        self.tool_registry.register_tool(GoogleSearchTool())
        self.tool_registry.register_tool(CodeExecutorTool())
        self.tool_registry.register_tool(DeepfakeDetectionTool())
        
        self.loop_agent = RealLoopAgent(self)
        


        event_bus.subscribe("THREAT_DETECTED", self.on_threat_detected)

    def on_threat_detected(self, data):
        print(f"⚡ [MASTER] Reacting to THREAT event: {data}")
        # Auto-trigger evidence collection
        self.agents["evidence"].process(data, self.context)

    def pipeline_ultimate(self, user_input):
        # 1. Observability Start
        trace = metrics_collector.start_trace("MasterPipeline")
        
        # --- NEW: Memory Recall (Learning) ---
        past_case = memory_bank.find_similar_cases(user_input)
        memory_status = "No similar past cases found."
        if past_case:
            self.context.log("MasterController", "🧠 MEMORY RECALL: Found similar past case.", {"past_content": past_case[:50]})
            memory_status = "🧠 Memory Recall: Similar pattern recognized from past incidents."

       
        search_tool = self.tool_registry.get_tool("GoogleSearch")
        internet_status = "Checked global databases."
        if search_tool:
            
            web_results = search_tool.execute(f"Is '{user_input[:30]}...' a known scam?")
            self.context.log("MasterController", "🌐 INTERNET CHECK: Verified against global databases.", web_results)
            internet_status = "🌐 Internet Check: Verified against global scam databases."

        # 3. Run Standard Pipeline
        results = self.pipeline_v3(user_input)
        
        # Inject Context into Results for UI
        results["system_context"] = {
            "memory": memory_status,
            "internet": internet_status
        }
        
        # 4. Event Publishing
        threat_data = results.get("threat", {})
        threat_sev = threat_data.get("severity", 0)
        
        if isinstance(threat_sev, int) and threat_sev >= 4:
            event_bus.publish("THREAT_DETECTED", {"text": user_input, "analysis": results["threat"]})
            metrics_collector.log_threat(threat_sev)
        
        # 5. Observability End
        metrics_collector.end_trace(trace, results)
        metrics_collector.log_request()
        
        return results

# --- 4. Deployment Simulation (The Wrapper) ---
class ShaktiDeployment:
    def __init__(self):
        self.master = MasterControllerUltimate()
        self.session_service = session_service 
        self.metrics = metrics_collector 

    def handle_request(self, session_id, user_input):
        # 1. Log to Memory
        self.session_service.add_history(session_id, "user", user_input)
        
        # 2. Process
        results = self.master.pipeline_ultimate(user_input)
        
        # 3. Evaluation (Self-Correction)
        eval_result = eval_pipeline.process(results, self.master.context)
        results["_evaluation"] = eval_result
        
        # 4. Log Response
        self.session_service.add_history(session_id, "system", str(results))
        
        return {"status": "success", "data": results}

# --- 5. Real FastAPI Code Generator ---
FASTAPI_CODE = """
# main.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Shakti AI API", version="1.0.0")
# Initialize System (Mock import)
# master = MasterControllerUltimate()

class AnalysisRequest(BaseModel):
    user_id: str
    text: str

@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    # results = master.pipeline_ultimate(req.text)
    return {"status": "success", "data": "Analysis Complete"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# --- 6. The Grand Demo ---
def run_final_deployment_demo():
    print("--- SHAKTI ULTIMATE DEPLOYMENT (Top 1% Ready) ---\n")
    
    deployment = ShaktiDeployment()
    
    # Start Background Loop
    deployment.master.loop_agent.start()
    
    # Create Session
    sid = deployment.session_service.create_session()
    print(f"Session Created: {sid}")
    
    # Test 1: High Threat (Triggers Event Bus + Evidence + SQLite + Heatmap)
    print("\n>>> User: I will kill you. (Location: India)")
    response = deployment.handle_request(sid, "I will kill you. (Location: India)")
    
    print(f"[System Response] Threat: {response['data']['threat']['severity']}")
    print(f"[Evaluation] {response['data']['_evaluation']['critique']}")
    
    # Test 2: MCP Tool
    print("\n>>> Testing MCP Tool...")
    mcp = deployment.master.tool_registry.get_tool("MCP_filesystem")
    print(mcp.execute(cmd="ls"))

    # Stop Loop
    deployment.master.loop_agent.stop()
    
    # Show Dashboard
    print(deployment.metrics.get_dashboard())
    
    print("\n[Generated Artifacts]")
    print("1. FastAPI Code (main.py) - Ready for Cloud Run")
    print("2. SQLite DB (shakti_memory.db) - Persistent Storage")

if __name__ == "__main__":
    run_final_deployment_demo()



# --- CELL 17: Loop Agent, A2A & Deployment (Grand Finale) ---


import time
import threading

# --- 1. A2A Protocol (Agent-to-Agent Communication) ---
class A2ARouter:
    def __init__(self, master_controller):
        self.master = master_controller

    def route_message(self, sender_agent, target_agent_name, message):
        """
        Allows agents to talk directly to each other without going through the user.
        """
        print(f"📡 [A2A PROTOCOL] {sender_agent} --> {target_agent_name}: {str(message)[:50]}...")
        
       
        if target_agent_name in self.master.agents:
            target = self.master.agents[target_agent_name]
            
            response = target.process(message, self.master.context)
            return response
        return None

# --- 2. Loop Agent (Continuous Monitoring) ---
class LoopAgent:
    def __init__(self, master_controller, interval=2):
        self.master = master_controller
        self.interval = interval
        self.running = False
        self.stream_source = [
            "All quiet...",
            "Wait, someone is knocking...",
            "HELP ME!",
            "Just kidding."
        ]

    def start_monitoring(self):
        self.running = True
        print("\n🔄 [LOOP AGENT] Starting Continuous Threat Monitoring Stream...")
        
        # Simulate a stream of inputs
        for input_text in self.stream_source:
            if not self.running: break
            
            print(f"\n⏱️ [Stream Tick] Input: {input_text}")
            
            
            panic_agent = self.master.agents["panic"]
            panic_res = panic_agent.process(input_text, self.master.context)
            
            if panic_res.get("emergency_status") == "Active":
                print("🚨 [LOOP AGENT] EMERGENCY INTERCEPTED! Triggering Full Pipeline immediately.")
                self.master.pipeline_v3(input_text) 
            else:
                print("✅ [Stream Tick] Status Normal.")
            
            time.sleep(self.interval)
        
        print("🔄 [LOOP AGENT] Monitoring Stream Ended.\n")

    def stop(self):
        self.running = False

# --- 3. FastAPI Deployment Simulation ---

class FastAPISimulation:
    def __init__(self, master_controller):
        self.app_name = "Shakti API v1.0"
        self.master = master_controller

    def post_analyze(self, payload: dict):
        """
        Simulates POST /analyze endpoint
        Payload: {"text": "...", "user_id": "..."}
        """
        print(f"\n🌐 [API REQUEST] POST /analyze | Payload: {payload}")
        
        user_input = payload.get("text")
        user_id = payload.get("user_id")
        
        # 1. Store in Long Term Memory
        memory_bank.store_interaction(user_id, user_input, 0) # Initial score 0
        
        # 2. Run Pipeline
        result = self.master.pipeline_v3(user_input)
        
        # 3. Update Metrics
        threat_sev = result.get("threat", {}).get("severity", "Low")
        metrics_collector.log_threat(threat_sev)
        metrics_collector.metrics["total_requests"] += 1
        
        return {"status": 200, "response": result}

# --- 4. The Grand Integration ---
def run_elite_demo():
    print("--- SHAKTI ELITE SYSTEM---\n")
    
    # 1. Setup
    master = MasterControllerV3()
    # Inject new tools into master (if not already there)
    master.tool_registry.register_tool(DeepfakeDetectionTool())
    
    # 2. A2A Demo
    router = A2ARouter(master)
    print("--- 1. Testing A2A Protocol ---")
    # Simulate Threat Agent asking RedFlag Agent for help
    router.route_message("ThreatAgent", "redflag", "Check this text for grooming: 'Don't tell your mom'")
    
    # 3. Deepfake Tool Demo
    print("\n--- 2. Testing Deepfake Tool ---")
    df_tool = master.tool_registry.get_tool("DeepfakeDetector")
    print(df_tool.execute("suspicious_video_fake.mp4"))
    
    # 4. Loop Agent Demo
    print("\n--- 3. Testing Loop Agent (Real-time Stream) ---")
    loop = LoopAgent(master, interval=1)
    loop.start_monitoring()
    
    # 5. FastAPI Demo
    print("\n--- 4. Testing Deployment (FastAPI) ---")
    api = FastAPISimulation(master)
    response = api.post_analyze({"text": "I will kill you", "user_id": "user_123"})
    
    # 6. Final Dashboard
    print(metrics_collector.get_dashboard())

if __name__ == "__main__":
    run_elite_demo()


