"""
scenarios.py - Comprehensive scenario definitions for SpeakWise AI.
Contains all required scenarios from Section 4 and interview types from Section 13.
"""

SCENARIOS = {
    # ------------------ SECTION 4 SCENARIOS ------------------
    "job_interview": {
        "id": "job_interview",
        "category": "Career & Professional",
        "title": "Job Interview",
        "role": "Senior Hiring Manager (Sarah Vance)",
        "badge": "💼 Career",
        "description": "Practice answering classic and challenging job interview questions with a discerning executive recruiter.",
        "starter_message": "Good morning. Please take a seat. Let's begin with a brief introduction. Tell me about yourself.",
        "coach_tip": "Keep your introduction concise (60-90 seconds). Mention your current role, key achievements with metrics, and why you are excited about this opportunity.",
        "dialogue_flow": [
            "You mentioned your experience in sales and projects. Can you explain one challenge you faced and how you solved it?",
            "That sounds like solid problem-solving. How do you prioritize deliverables when multiple high-stakes deadlines collide?",
            "Where do you see your technical and leadership skills growing over the next 2-3 years?",
            "Finally, do you have any questions for me about the team, culture, or our expectations for this position?"
        ]
    },
    "hr_interview": {
        "id": "hr_interview",
        "category": "Career & Professional",
        "title": "HR Interview",
        "role": "Human Resources Director (Rachel Adams)",
        "badge": "👥 People",
        "description": "Focus on cultural fit, work ethic, interpersonal dynamics, and team conflict resolution.",
        "starter_message": "Hello Rohit! Welcome to our HR round. Why don't you share what initially attracted you to our organization's culture?",
        "coach_tip": "Connect your personal values with the company's mission statement. Use positive, forward-looking language.",
        "dialogue_flow": [
            "That aligns well with our vision. Can you describe a situation where you had a disagreement with a colleague and how you reached a compromise?",
            "What kind of management style brings out the highest productivity in you?",
            "Where do you see yourself contributing most during your first 90 days with us?"
        ]
    },
    "client_meeting": {
        "id": "client_meeting",
        "category": "Business Communication",
        "title": "Client Meeting",
        "role": "Key Account Client (Elena Rostova)",
        "badge": "🤝 Business",
        "description": "Present solutions, address client reservations diplomatically, and manage project scope.",
        "starter_message": "Good morning Rohit. We reviewed your initial proposal. While the feature list looks promising, we have serious reservations regarding the delivery timeline and cost structure. How do you propose we address this?",
        "coach_tip": "Acknowledge client concerns before offering solutions. Use diplomatic phrasing like 'We can explore a phased delivery model'.",
        "dialogue_flow": [
            "A phased delivery sounds interesting. What specific milestones could we expect within the first month?",
            "How will your team ensure that our internal data security policies are strictly upheld throughout?",
            "Excellent. Let's draft a revised scope memorandum to review with our executive board."
        ]
    },
    "manager_conversation": {
        "id": "manager_conversation",
        "category": "Workplace Communication",
        "title": "Manager Conversation",
        "role": "Direct Manager (David Chen)",
        "badge": "👔 Leadership",
        "description": "Discuss quarterly goals, align on sprint priorities, or communicate workload challenges.",
        "starter_message": "Hey Rohit, thanks for scheduling this 1-on-1. How are things tracking for you this week, and what's top of mind for our sync today?",
        "coach_tip": "Be proactive and solutions-oriented. Frame workload bottlenecks in terms of trade-offs rather than complaints.",
        "dialogue_flow": [
            "I appreciate the honesty. How are our release dates looking for the deliverables scheduled for this Friday?",
            "If we need to reprioritize some items to avoid burnout, which module would you recommend deferring to next sprint?",
            "Understood. Let me know what roadblocks I can clear with senior management for you."
        ]
    },
    "team_meeting": {
        "id": "team_meeting",
        "category": "Workplace Communication",
        "title": "Team Meeting",
        "role": "Scrum Master (Ananya Sharma)",
        "badge": "👥 Standup",
        "description": "Participate actively in a daily standup or sprint retrospective, sharing progress concisely.",
        "starter_message": "Good morning team! Let's kick off our daily standup. Rohit, you're up first. What did you accomplish yesterday, what's planned for today, and do you have any blockers?",
        "coach_tip": "Keep your update under 90 seconds. Be precise with deliverables and mention cross-team dependencies clearly.",
        "dialogue_flow": [
            "Thanks for the clear summary. Does your API task have any dependency on Deepak's database migrations?",
            "Would you like to do a quick 5-minute technical sync with Deepak immediately after this standup?",
            "Sounds great! Keep up the good momentum."
        ]
    },
    "sales_call": {
        "id": "sales_call",
        "category": "Business Communication",
        "title": "Sales Call",
        "role": "Prospective Enterprise Buyer (Mark Higgins)",
        "badge": "📈 Sales",
        "description": "Pitch a SaaS product, understand buyer pain points, and handle price objections smoothly.",
        "starter_message": "Hi Rohit, I have about 10 minutes before my next meeting. Your email mentioned your platform can cut our cloud compute costs by 30%. How exactly does it work?",
        "coach_tip": "Lead with the customer's pain point and ROI metrics rather than technical jargon. Ask clarifying questions.",
        "dialogue_flow": [
            "We currently use another enterprise vendor. What makes your solution distinct enough to warrant switching?",
            "That sounds compelling, but what does the onboarding and migration timeline look like for an enterprise team our size?",
            "Fair points. Send over your case study deck and pricing tiers, and let's set up a technical trial."
        ]
    },
    "customer_complaint": {
        "id": "customer_complaint",
        "category": "Soft Skills & EQ",
        "title": "Customer Complaint",
        "role": "Frustrated Customer (Robert Miller)",
        "badge": "🔥 De-escalation",
        "description": "De-escalate tension with an upset customer, display empathy, and offer constructive resolution.",
        "starter_message": "This is the third time this week your service has experienced downtime during our peak operating hours! It's costing our business thousands of dollars. What are you going to do about this right now?!",
        "coach_tip": "Use the LAST method: Listen, Apologize with empathy, Solve the issue, and Thank them for raising it. Do not be defensive.",
        "dialogue_flow": [
            "I hear your apology, but how can you guarantee this won't repeat tomorrow morning during our busiest shift?",
            "Will your engineering lead provide an incident post-mortem report by tomorrow?",
            "Alright. I appreciate your calm, prompt handling of this. Please email me the confirmation as soon as the patch is verified."
        ]
    },
    "networking": {
        "id": "networking",
        "category": "Soft Skills & EQ",
        "title": "Networking",
        "role": "Industry Leader (Victoria Sterling)",
        "badge": "🥂 Connection",
        "description": "Deliver a crisp elevator pitch and build professional rapport at a conference mixer.",
        "starter_message": "Hello there! I noticed you were attending the AI Innovation keynote earlier. Great session, wasn't it? What brings you to the summit this year?",
        "coach_tip": "State your specialty, current impactful initiative, and ask an open question to create genuine 2-way dialogue.",
        "dialogue_flow": [
            "That is a very dynamic domain to be working in. What is the most exciting breakthrough your team is exploring?",
            "Fascinating perspective. Have you published or presented on that topic before?",
            "It was a pleasure speaking with you, Rohit. Let's exchange details on LinkedIn and stay connected."
        ]
    },
    "presentation": {
        "id": "presentation",
        "category": "Career & Professional",
        "title": "Presentation",
        "role": "Executive Board Evaluator (Prof. Kenneth Green)",
        "badge": "📽️ Public Speaking",
        "description": "Open a presentation with a strong hook, outline key points, and handle tough Q&A.",
        "starter_message": "Good afternoon everyone. Rohit is now presenting our quarterly strategic roadmap. Rohit, the floor is yours whenever you are ready.",
        "coach_tip": "Start with a compelling hook or problem statement. Outline your 3 agenda points clearly before diving into details.",
        "dialogue_flow": [
            "Thank you for the thorough overview. Looking at your financial projection slide, what assumptions did you make regarding customer churn?",
            "How does this initiative align with our broader ESG and sustainability objectives for this fiscal year?",
            "Very clear and composed responses. Thank you, Rohit."
        ]
    },
    "asking_for_leave": {
        "id": "asking_for_leave",
        "category": "Workplace Communication",
        "title": "Asking for Leave",
        "role": "Team Lead (Priya Nair)",
        "badge": "🏖️ Requests",
        "description": "Request planned time off or emergency leave while ensuring team coverage and project continuity.",
        "starter_message": "Hi Rohit, I saw your ping about requesting some time off. What dates were you looking at, and how is your sprint workload being handed over?",
        "coach_tip": "State clear dates, confirm that urgent tasks are covered by teammates, and provide an emergency contact method.",
        "dialogue_flow": [
            "Those dates look manageable. Have you synced with any teammate to take over your on-call duties while you're away?",
            "Great. Could you make sure the documentation in our tracker is updated before you head out?",
            "Sounds like a plan! Have a restful break, Rohit."
        ]
    },
    "salary_negotiation": {
        "id": "salary_negotiation",
        "category": "Career & Professional",
        "title": "Salary Negotiation",
        "role": "Compensation Partner (Jonathan Vance)",
        "badge": "💵 Negotiation",
        "description": "Articulate your market value, negotiate compensation respectfully, and present tangible contributions.",
        "starter_message": "Congratulations again on receiving our offer for the Senior Consultant position, Rohit. We offered an annual base of $95,000 with standard bonuses. Did you have any questions regarding the offer package?",
        "coach_tip": "Express enthusiasm first. Back your counteroffer with market benchmarks and your specific projected impact.",
        "dialogue_flow": [
            "I understand you are targeting closer to $110,000 based on industry benchmarks. Can you elaborate on the specific skills or past results that justify this adjustment?",
            "If base salary has internal equity caps, would you be open to a combination of sign-on bonus and performance equity grants?",
            "That is a reasonable structure. Let me take this revised framework to the executive committee for approval."
        ]
    },
    "college_viva": {
        "id": "college_viva",
        "category": "Academic",
        "title": "College Viva",
        "role": "External Examiner (Dr. Aris Thorne)",
        "badge": "🎓 Academic",
        "description": "Defend your final year capstone thesis, explain architecture decisions, and demonstrate theoretical mastery.",
        "starter_message": "Welcome to your capstone defense, Rohit. Please state the title of your project and summarize the primary research problem you solved.",
        "coach_tip": "Be formal, academic, and structured. Clearly define the problem statement, methodology, and empirical results.",
        "dialogue_flow": [
            "Why did you choose this specific architectural framework over traditional alternatives for handling high concurrency?",
            "What were the primary edge cases you tested during your benchmarking phase?",
            "Well articulated and defended. That concludes your viva examination."
        ]
    },
    "group_discussion": {
        "id": "group_discussion",
        "category": "Academic",
        "title": "Group Discussion",
        "role": "GD Moderator (Dr. Meera Sen)",
        "badge": "🗣️ Debate",
        "description": "Contribute balanced viewpoints, agree or disagree courteously, and synthesize arguments in a GD.",
        "starter_message": "Welcome everyone to today's group discussion. The topic before the panel is: 'Will Generative AI create more sustainable jobs than it displaces over the next decade?' Rohit, please initiate your thoughts.",
        "coach_tip": "Structure your answer: Hook, Point, Evidence/Example, Conclusion. Use phrases like 'While that is a valid point, we must also consider...'",
        "dialogue_flow": [
            "An interesting point on productivity gains. Another participant argued that junior roles will face significant contraction. How do you respond to that?",
            "How do you propose educational institutions restructure their curricula to prepare graduates for this transformation?",
            "Well reasoned and structured. Thank you for contributing to the discussion."
        ]
    },

    # ------------------ SECTION 13 INTERVIEW PRACTICE SCENARIOS ------------------
    "interview_hr": {
        "id": "interview_hr",
        "category": "Interview Track",
        "title": "HR Interview",
        "role": "Senior HR Manager (Linda Campbell)",
        "badge": "🎯 HR Track",
        "description": "Comprehensive HR behavioral round covering values, situational judgment, and culture fit.",
        "starter_message": "Good morning Rohit, welcome to our HR behavioral interview. Tell me about yourself and what motivates your career choices.",
        "coach_tip": "Structure your answer with your background, personal drive, and alignment with our company values.",
        "dialogue_flow": [
            "Why should we hire you over other qualified candidates who applied for this role?",
            "Tell me about a difficult interpersonal situation you handled on a past team.",
            "Where do you see yourself professionally in five years?"
        ]
    },
    "interview_ba": {
        "id": "interview_ba",
        "category": "Interview Track",
        "title": "Business Analyst Interview",
        "role": "Director of Analytics (Arthur Pendelton)",
        "badge": "📊 BA Track",
        "description": "Questions on requirements elicitation, stakeholder management, metrics, and data modeling.",
        "starter_message": "Welcome Rohit. In this Business Analyst interview, please walk me through your process for translating ambiguous business requirements into actionable functional specs.",
        "coach_tip": "Explain elicitation techniques (user stories, workshops) and validation methods (traceability matrix).",
        "dialogue_flow": [
            "How do you resolve conflicting priorities between product management and engineering when scope is tight?",
            "Can you describe a time when data contradicted a senior stakeholder's intuition? How did you present your findings?",
            "What KPIs do you track to measure the post-launch success of a business feature?"
        ]
    },
    "interview_marketing": {
        "id": "interview_marketing",
        "category": "Interview Track",
        "title": "Marketing Interview",
        "role": "Chief Marketing Officer (Gwen Stacy)",
        "badge": "📣 Marketing Track",
        "description": "Questions on campaign strategy, CAC/LTV, brand positioning, and content funnels.",
        "starter_message": "Hello Rohit! Glad to have you here. Could you share an overview of a high-impact marketing campaign you spearheaded from concept to execution?",
        "coach_tip": "Focus on the target audience persona, distribution channels, and measurable ROI (CAC, conversion rates).",
        "dialogue_flow": [
            "How do you balance short-term performance marketing with long-term brand equity building?",
            "If your acquisition cost spiked by 40% on paid search, what diagnostic steps would you take immediately?",
            "How do you incorporate storytelling into B2B marketing collateral?"
        ]
    },
    "interview_sales": {
        "id": "interview_sales",
        "category": "Interview Track",
        "title": "Sales Interview",
        "role": "VP of Global Sales (Derek Sterling)",
        "badge": "🎯 Sales Track",
        "description": "Focus on pipeline management, closing techniques, prospecting, and quota attainment.",
        "starter_message": "Hi Rohit. In enterprise sales, persistence and qualification are everything. Walk me through your largest closed deal and how you navigated the procurement cycle.",
        "coach_tip": "Highlight MEDDIC or BANT qualification, identifying economic buyers, and overcoming stall objections.",
        "dialogue_flow": [
            "How do you handle a prospect who stops responding after receiving the final commercial proposal?",
            "What is your philosophy on prospecting and filling your top of funnel when inbound leads are slow?",
            "Sell me on why you will consistently hit 100%+ quota attainment on our team."
        ]
    },
    "interview_data": {
        "id": "interview_data",
        "category": "Interview Track",
        "title": "Data Analytics Interview",
        "role": "Lead Data Scientist (Dr. Raymond Scott)",
        "badge": "📉 Analytics Track",
        "description": "Evaluate analytical thinking, statistical interpretation, data pipeline understanding, and stakeholder storytelling.",
        "starter_message": "Hello Rohit! To begin our Data Analytics technical discussion, could you share a complex dataset you analyzed and how your insights altered business strategy?",
        "coach_tip": "Lead with the business impact, then explain the data cleaning, exploratory analysis, and visualization techniques.",
        "dialogue_flow": [
            "How do you ensure data integrity and detect anomalous outliers when processing multi-source pipelines?",
            "Explain how you would communicate the uncertainty or confidence interval of a forecast to non-technical business leaders.",
            "What is your approach when a stakeholder wants to cherry-pick metrics to confirm their bias?"
        ]
    },
    "interview_management": {
        "id": "interview_management",
        "category": "Interview Track",
        "title": "General Management Interview",
        "role": "Executive Managing Director (Claire Redfield)",
        "badge": "🏛️ Management Track",
        "description": "Examine strategic vision, P&L ownership, cross-functional leadership, and organizational development.",
        "starter_message": "Welcome Rohit. General Management requires balancing strategic vision with operational execution. Tell me about a time you led a cross-functional team through a major organizational change.",
        "coach_tip": "Emphasize change management, continuous stakeholder communication, empathetic leadership, and clear milestones.",
        "dialogue_flow": [
            "How do you cultivate psychological safety on a high-performing team while holding individuals strictly accountable for KPIs?",
            "If two department heads under your leadership reached an operational deadlock on resource allocation, how would you resolve it?",
            "What frameworks do you use to evaluate trade-offs between short-term quarterly revenue and long-term innovation?"
        ]
    },

    # ------------------ FREE CONVERSATION ------------------
    "free_conversation": {
        "id": "free_conversation",
        "category": "General Practice",
        "title": "Free Conversation",
        "role": "AI Communication Coach (Alex)",
        "badge": "💬 Free Flow",
        "description": "Casual, engaging conversation adapted to your fluency level with real-time soft-skills coaching.",
        "starter_message": "Hi! I'm your AI communication coach. What was the most interesting thing that happened to you this week?",
        "coach_tip": "Express yourself naturally. Speak about hobbies, news, weekend plans, or personal achievements.",
        "dialogue_flow": [
            "That sounds fascinating! What inspired you to pursue that interest or activity?",
            "How do you usually manage your time between that and your daily responsibilities?",
            "If you could recommend one book, podcast, or experience related to that, what would it be and why?"
        ]
    }
}


def get_scenario(scenario_id: str) -> dict:
    return SCENARIOS.get(scenario_id, SCENARIOS["job_interview"])


def get_all_scenarios() -> list:
    return list(SCENARIOS.values())


def get_scenarios_by_category() -> dict:
    grouped = {}
    for s in SCENARIOS.values():
        cat = s.get("category", "General Practice")
        grouped.setdefault(cat, []).append(s)
    return grouped
