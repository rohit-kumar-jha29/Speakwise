"""
challenges.py - Interactive challenges for Grammar, Vocabulary, and Situation modes.
"""

GRAMMAR_CHALLENGES = [
    {
        "id": "g1",
        "category": "Tenses & Duration",
        "prompt": "Find and correct the grammatical error in this sentence:",
        "sentence": "I am working in this company since three years.",
        "correct_answer": "I have been working in this company for three years.",
        "accepted_variants": [
            "I have worked in this company for three years.",
            "I've been working at this company for three years.",
            "I have been working at this company for three years."
        ],
        "explanation": "Use the Present Perfect Continuous ('have been working') to describe an action that started in the past and continues into the present. Also, use 'for' (not 'since') when referring to a duration of time (three years).",
        "rule_summary": "Present Perfect Continuous + 'for' duration"
    },
    {
        "id": "g2",
        "category": "Subject-Verb Agreement",
        "prompt": "Correct the subject-verb agreement error:",
        "sentence": "Each of the team members have submitted their report on time.",
        "correct_answer": "Each of the team members has submitted their report on time.",
        "accepted_variants": [
            "Each of the team members has submitted his or her report on time."
        ],
        "explanation": "'Each' is grammatically singular and requires a singular verb ('has submitted', not 'have submitted').",
        "rule_summary": "'Each' takes a singular verb ('has')"
    },
    {
        "id": "g3",
        "category": "Prepositions & Phrasal Verbs",
        "prompt": "Correct the preposition and phrasing error:",
        "sentence": "Please revert back to me as soon as you will receive the file.",
        "correct_answer": "Please get back to me as soon as you receive the file.",
        "accepted_variants": [
            "Please revert to me as soon as you receive the file.",
            "Please reply to me as soon as you receive the file.",
            "Please get back to me as soon as you get the file."
        ],
        "explanation": "'Revert back' is redundant ('revert' already means return). In time clauses starting with 'as soon as', use the simple present ('receive'), not the future tense ('will receive').",
        "rule_summary": "Avoid redundant 'back' with revert + simple present in time clauses"
    },
    {
        "id": "g4",
        "category": "Conditionals",
        "prompt": "Correct this hypothetical third conditional sentence:",
        "sentence": "If I would have known about the meeting, I would attend it.",
        "correct_answer": "If I had known about the meeting, I would have attended it.",
        "accepted_variants": [
            "Had I known about the meeting, I would have attended it.",
            "If I had known about the meeting, I'd have attended it."
        ],
        "explanation": "In a third conditional (past hypothetical), the 'if' clause takes the Past Perfect ('had known'), and the main clause takes 'would have + past participle' ('would have attended').",
        "rule_summary": "Third conditional: If + had + V3, would have + V3"
    },
    {
        "id": "g5",
        "category": "Articles & Nouns",
        "prompt": "Correct the article and pluralization mistake:",
        "sentence": "Can you give me an advice regarding my career informations?",
        "correct_answer": "Can you give me some advice regarding my career information?",
        "accepted_variants": [
            "Can you give me a piece of advice regarding my career information?",
            "Could you give me some advice regarding my career information?"
        ],
        "explanation": "'Advice' and 'information' are uncountable nouns in English. They do not take the indefinite article 'an', nor do they have a plural form ('informations' is incorrect).",
        "rule_summary": "Uncountable nouns: advice & information (no 'an' or 's')"
    },
    {
        "id": "g6",
        "category": "Professional Phrasing",
        "prompt": "Fix the awkward phrasing to make it standard business English:",
        "sentence": "Can we prepone the sync meeting to 2 PM?",
        "correct_answer": "Can we move the sync meeting forward to 2 PM?",
        "accepted_variants": [
            "Could we move the sync meeting forward to 2 PM?",
            "Can we advance the sync meeting to 2 PM?",
            "Could we reschedule the sync meeting earlier to 2 PM?"
        ],
        "explanation": "While 'prepone' is used in Indian English, international business English prefers 'move forward', 'bring forward', or 'reschedule earlier'.",
        "rule_summary": "'Prepone' -> 'move forward' or 'bring forward'"
    }
]

VOCABULARY_CHALLENGES = [
    {
        "id": "v1",
        "word": "Meticulous",
        "part_of_speech": "Adjective",
        "definition": "Showing great attention to detail; very careful and precise.",
        "synonyms": ["Thorough", "Scrupulous", "Painstaking", "Diligent"],
        "example": "Her meticulous review of the financial audit caught three critical accounting discrepancies.",
        "prompt": "Write a professional sentence about reviewing work or organizing a project using the word 'meticulous'.",
        "ideal_usage_hint": "Pair it with nouns like 'planning', 'preparation', 'research', or 'attention to detail'."
    },
    {
        "id": "v2",
        "word": "Eloquent",
        "part_of_speech": "Adjective",
        "definition": "Fluent or persuasive in speaking or writing; clearly expressing an idea.",
        "synonyms": ["Articulate", "Expressive", "Persuasive", "Poignant"],
        "example": "His eloquent presentation convinced the venture capital board to greenlight the funding.",
        "prompt": "Write a sentence describing an impactful speech, proposal, or speaker using 'eloquent'.",
        "ideal_usage_hint": "Use it to describe a pitch, an advocate, an explanation, or a speaker."
    },
    {
        "id": "v3",
        "word": "Streamline",
        "part_of_speech": "Verb",
        "definition": "To make an organization, system, or process simpler and more effective by removing unnecessary steps.",
        "synonyms": ["Optimize", "Simplify", "Rationalize", "Expedite"],
        "example": "We adopted automated CI/CD pipelines to streamline our deployment cycle from hours to minutes.",
        "prompt": "Write a sentence describing how you or your team improved a workflow or process using 'streamline'.",
        "ideal_usage_hint": "Mention a specific tool or methodology that eliminated friction or reduced turnaround time."
    },
    {
        "id": "v4",
        "word": "Diplomatic",
        "part_of_speech": "Adjective",
        "definition": "Able to handle difficult situations or negotiations tactfully and without offending others.",
        "synonyms": ["Tactful", "Polite", "Discreet", "Judicious"],
        "example": "She handled the client's demanding feedback with a diplomatic response that preserved the contract.",
        "prompt": "Write a sentence about resolving a disagreement or handling an upset stakeholder using 'diplomatic'.",
        "ideal_usage_hint": "Emphasize remaining calm, finding mutual ground, or delivering delicate news."
    },
    {
        "id": "v5",
        "word": "Ambiguous",
        "part_of_speech": "Adjective",
        "definition": "Open to more than one interpretation; unclear or vague.",
        "synonyms": ["Equivocal", "Indefinite", "Obscure", "Enigmatic"],
        "example": "Because the project requirements were ambiguous, the engineering team requested a clarification workshop.",
        "prompt": "Write a sentence explaining how unclear instructions or terms were resolved using 'ambiguous'.",
        "ideal_usage_hint": "Highlight seeking clarification when specifications or emails lack precise detail."
    }
]

SITUATION_CHALLENGES = [
    {
        "id": "s1",
        "title": "Missing a Critical Project Deadline",
        "difficulty": "Intermediate",
        "context": "You realize that due to an unexpected technical roadblock, you will not be able to finish your sprint deliverable by the 5:00 PM deadline today. You need to write a Slack message or email to your direct manager.",
        "task": "Write your communication to your manager explaining the delay diplomatically, stating what happened, and offering a revised timeline.",
        "key_competencies": ["Accountability", "Proactivity", "Solution-oriented framing", "Diplomatic urgency"],
        "model_answer": "Hi David, I wanted to give you an urgent update regarding today's 5 PM deliverable. While testing the payment gateway integration, we uncovered an edge-case concurrency error that requires thorough debugging to ensure security. As a result, we will need an additional four hours to test thoroughly. I estimate having the complete build ready for review by tomorrow at 10 AM. I apologize for the delay and am happy to jump on a quick 5-minute call if you would like me to walk you through the details.",
        "evaluation_rubric": {
            "lead_with_update": "Did the user inform the manager ahead of time rather than after the deadline passed?",
            "clear_reason": "Did the user provide a factual reason without making flimsy excuses?",
            "new_eta": "Did the user commit to a specific revised delivery time?",
            "professional_courtesy": "Was the tone polite, responsible, and solution-focused?"
        }
    },
    {
        "id": "s2",
        "title": "Turning Down Extra Work Politely (Saying No to a Colleague)",
        "difficulty": "Intermediate",
        "context": "A colleague asks you to take over reviewing a 50-page technical specification document today, but your plate is completely full with high-priority sprint tasks committed to your team.",
        "task": "Respond to your colleague refusing the request respectfully while preserving a collaborative relationship.",
        "key_competencies": ["Assertiveness", "Setting professional boundaries", "Offering alternatives"],
        "model_answer": "Hi Sarah, thank you for thinking of me for this review. Unfortunately, I'm completely booked with our sprint deliverables due by end-of-day today and won't be able to give your document the attention it deserves. If Thursday works for you, I'd be more than happy to review it then, or perhaps Alex from the QA group might have availability today?",
        "evaluation_rubric": {
            "polite_acknowledgment": "Thanked or acknowledged the request pleasantly",
            "clear_boundary": "Gave a clear 'no' based on workload without being aggressive",
            "alternative_offered": "Suggested a later date or another resource to be helpful"
        }
    },
    {
        "id": "s3",
        "title": "Asking for Constructive Feedback After an Interview",
        "difficulty": "Advanced",
        "context": "You received a polite rejection email for a Senior Analyst position you really wanted. You want to reply asking for specific areas you can improve for future roles without sounding bitter.",
        "task": "Write an email to the recruiter thanking them and requesting constructive feedback on your candidacy.",
        "key_competencies": ["Growth mindset", "Grace under disappointment", "Professional relationship maintenance"],
        "model_answer": "Dear Ms. Vance, Thank you for getting back to me regarding the Senior Analyst position. While I am naturally disappointed not to be joining your team at this stage, I genuinely enjoyed learning more about your organization's vision. As I am continually striving to refine my skills, I would be immensely grateful if you or the panel could share one or two specific areas where I could strengthen my background or interview performance for future consideration. Thank you again for your time and guidance, and I hope our paths cross again.",
        "evaluation_rubric": {
            "graceful_response": "Acknowledged the outcome with dignity and gratitude",
            "low_friction_request": "Framed feedback as a modest, constructive question (1-2 points)",
            "long_term_networking": "Kept the door open for future opportunities"
        }
    }
]
