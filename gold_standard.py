GOLD_STANDARD = [

    # ── DIRECT MODULE LOOKUPS ─────────────────────────────────
    {
        "id": "Q01",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "What is the module Advanced Machine Learning about?",
        "gold_answer": (
            "Advanced Machine Learning (M1552) covers neural networks, "
            "backpropagation, CNNs, RNNs, GANs, Autoencoders and Transformers. "
            "It is worth 6 CP, examined by a 90-minute written exam, "
            "and taught in English in the winter semester."
        ),
        # NEW: The exact chunk we EXPECT the retriever to find.
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q02",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "How many credit points is the Advanced Machine Learning module worth?",
        "gold_answer": "6 credit points (CP).",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q03",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "What are the recommended prerequisites for Advanced Machine Learning?",
        "gold_answer": (
            "Mathematics I-III, Numerical Mathematics / Numerics, "
            "and programming skills preferably in Python."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q04",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "Who is responsible for the Advanced Machine Learning module at TUHH?",
        "gold_answer": "Dr. Jens-Peter Zemke.",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q05",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "What type of examination does the Advanced Machine Learning module use?",
        "gold_answer": "Written exam, 90 minutes.",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q06",
        "category": "direct_module",
        "difficulty": "medium",
        "query": "What topics are taught in the Advanced Machine Learning lecture?",
        "gold_answer": (
            "Basics of neural nets; feedforward networks and backpropagation; "
            "CNNs; RNNs; adversarial attacks; residual networks; neural ODEs; "
            "autoencoders; GANs; attention and transformers."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q07",
        "category": "direct_module",
        "difficulty": "easy",
        "query": "In which semester is the Advanced Machine Learning course offered?",
        "gold_answer": "Winter semester (WiSe).",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },

    # ── CURRICULUM STRUCTURE ──────────────────────────────────
    {
        "id": "Q08",
        "category": "curriculum_structure",
        "difficulty": "medium",
        "query": "Is Advanced Machine Learning compulsory for Data Science students?",
        "gold_answer": (
            "Yes — it is listed as Core Qualification: Compulsory "
            "in the Data Science curriculum."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q09",
        "category": "curriculum_structure",
        "difficulty": "medium",
        "query": "Which TUHH programs include Advanced Machine Learning in their curriculum?",
        "gold_answer": (
            "Computational Methods and Machine Learning in Engineering, "
            "Computer Science, Data Science, Interdisciplinary Mathematics, "
            "Mechatronics, Technomathematics I and II, and "
            "Theoretical Mechanical Engineering."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q10",
        "category": "curriculum_structure",
        "difficulty": "medium",
        "query": "What is the workload for the Advanced Machine Learning module?",
        "gold_answer": (
            "Total workload 124 hours: Independent Study Time 62 h + "
            "Study Time in Lecture 28 h for the course component."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q11",
        "category": "curriculum_structure",
        "difficulty": "medium",
        "query": "How many hours per week is the Advanced Machine Learning lecture?",
        "gold_answer": "2 hours/week lecture + 2 hours/week recitation (small group) = 4 hrs/wk total.",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q12",
        "category": "curriculum_structure",
        "difficulty": "hard",
        "query": "What is the difference between Core Qualification and Elective modules in the Data Science program?",
        "gold_answer": (
            "Core Qualification modules are compulsory for all program students. "
            "Elective modules are optional and allow specialisation in a sub-field."
        ),
        # Broad program question, target is the general handbook
        "target_module": "Data Science Program",
        "target_code": None,
    },
    {
        "id": "Q13",
        "category": "curriculum_structure",
        "difficulty": "hard",
        "query": "How many total credit points are needed to finish the Data Science master?",
        "gold_answer": "120 credit points — standard for a 4-semester German M.Sc.",
        "target_module": "Data Science Program",
        "target_code": None,
    },

    # ── RECOMMENDATION ────────────────────────────────────────
    {
        "id": "Q14",
        "category": "recommendation",
        "difficulty": "medium",
        "query": "I love mathematics and programming. What should I study at TUHH?",
        "gold_answer": (
            "Data Science or Computer Science would suit you well — both require "
            "strong mathematical foundations and programming (Python)."
        ),
        # Can be multiple correct targets
        "target_module": ["Data Science", "Computer Science"],
        "target_code": None,
    },
    {
        "id": "Q15",
        "category": "recommendation",
        "difficulty": "easy",
        "query": "I am interested in deep learning and neural networks. Which module covers that?",
        "gold_answer": (
            "Advanced Machine Learning (M1552) directly covers deep learning: "
            "CNNs, RNNs, GANs, Autoencoders, and Transformers."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q16",
        "category": "recommendation",
        "difficulty": "medium",
        "query": "I want to understand Generative Adversarial Networks. What module should I take?",
        "gold_answer": (
            "Advanced Machine Learning (M1552) covers GANs and Autoencoders "
            "as part of its lecture content."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q17",
        "category": "recommendation",
        "difficulty": "hard",
        "query": "I want to work in AI research after my master. What should I focus on at TUHH?",
        "gold_answer": (
            "Focus on the Data Science core qualification modules especially "
            "Advanced Machine Learning, supplement with research-track electives, "
            "and invest heavily in your master thesis."
        ),
        "target_module": ["Data Science", "Advanced Machine Learning"],
        "target_code": "M1552",
    },
    {
        "id": "Q18",
        "category": "recommendation",
        "difficulty": "medium",
        "query": "I enjoy working in teams and group projects. Are there modules with teamwork?",
        "gold_answer": (
            "Yes — Advanced Machine Learning explicitly develops social competence: "
            "joint solutions in small teams and group development of ideas."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q19",
        "category": "recommendation",
        "difficulty": "hard",
        "query": "I come from a physics background. Can I apply for the Data Science program?",
        "gold_answer": (
            "Physics graduates typically have the required mathematical background "
            "(analysis, linear algebra, numerics) aligned with recommended prerequisites."
        ),
        "target_module": "Data Science Program",
        "target_code": None,
    },
    {
        "id": "Q20",
        "category": "recommendation",
        "difficulty": "medium",
        "query": "Which modules involve Python programming at TUHH?",
        "gold_answer": (
            "Advanced Machine Learning explicitly recommends Python. "
            "Most Data Science core modules also use Python for implementations."
        ),
        "target_module": ["Advanced Machine Learning", "Data Science"],
        "target_code": "M1552",
    },

    # ── LOGISTICS ─────────────────────────────────────────────
    {
        "id": "Q21",
        "category": "logistics",
        "difficulty": "easy",
        "query": "Is the Advanced Machine Learning course taught in English or German?",
        "gold_answer": "English (language code EN).",
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q22",
        "category": "logistics",
        "difficulty": "easy",
        "query": "How long is the Master of Science Data Science program at TUHH?",
        "gold_answer": "4 semesters (2 years).",
        "target_module": "Data Science Program",
        "target_code": None,
    },
    {
        "id": "Q23",
        "category": "logistics",
        "difficulty": "medium",
        "query": "What are the admission requirements for the Data Science master at TUHH?",
        "gold_answer": (
            "A relevant bachelor's degree with sufficient mathematical background. "
            "Individual module admission requirements are listed as 'None'."
        ),
        "target_module": ["Data Science Program", "Advanced Machine Learning"],
        "target_code": "M1552",
    },
    {
        "id": "Q24",
        "category": "logistics",
        "difficulty": "easy",
        "query": "What literature is recommended for the Advanced Machine Learning module?",
        "gold_answer": (
            "Script by the lecturer; online resources including "
            "neuralnetworksanddeeplearning.com and deeplearningbook.org."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },

    # ── COMPARATIVE / MULTI-PROGRAM ───────────────────────────
    {
        "id": "Q25",
        "category": "comparative",
        "difficulty": "hard",
        "query": "What is the difference between Data Science and Computer Science programs at TUHH?",
        "gold_answer": (
            "Both share modules like Advanced Machine Learning. "
            "Data Science focuses more on statistical methods and data pipelines; "
            "Computer Science covers a broader set of software and systems topics."
        ),
        "target_module": ["Data Science", "Computer Science"],
        "target_code": None,
    },
    {
        "id": "Q26",
        "category": "comparative",
        "difficulty": "medium",
        "query": "Which programs at TUHH share the Advanced Machine Learning module?",
        "gold_answer": (
            "Computational Methods and Machine Learning in Engineering, "
            "Computer Science, Data Science, Interdisciplinary Mathematics, "
            "Mechatronics, Technomathematics I and II, "
            "Theoretical Mechanical Engineering."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
    {
        "id": "Q27",
        "category": "comparative",
        "difficulty": "hard",
        "query": "Which TUHH programs involve machine learning?",
        "gold_answer": (
            "Data Science, Computer Science, Computational Methods and Machine "
            "Learning in Engineering, Mechatronics, and Technomathematics all "
            "include machine learning modules."
        ),
        "target_module": ["Data Science", "Computer Science", "Mechatronics", "Technomathematics"],
        "target_code": None,
    },
    {
        "id": "Q28",
        "category": "comparative",
        "difficulty": "hard",
        "query": "What skills will I have after completing the Data Science master?",
        "gold_answer": (
            "Professional knowledge: classify state-of-the-art neural networks. "
            "Practical skills: implement and apply neural networks to new domains. "
            "Social: collaborate in small teams. Autonomy: self-direct work and "
            "assess correctness independently."
        ),
        "target_module": ["Data Science", "Advanced Machine Learning"],
        "target_code": "M1552",
    },
    {
        "id": "Q29",
        "category": "comparative",
        "difficulty": "hard",
        "query": "I want to combine engineering with advanced mathematics. What do you recommend?",
        "gold_answer": (
            "Technomathematics or Interdisciplinary Mathematics combine rigorous "
            "mathematics with engineering applications. Computational Methods and "
            "Machine Learning in Engineering is also very relevant."
        ),
        "target_module": ["Technomathematics", "Interdisciplinary Mathematics"],
        "target_code": None,
    },
    {
        "id": "Q30",
        "category": "comparative",
        "difficulty": "hard",
        "query": "Are there modules compulsory across multiple TUHH master programs?",
        "gold_answer": (
            "Yes. Advanced Machine Learning (M1552) is compulsory in both "
            "Data Science (Core Qualification) and in Computational Methods "
            "and Machine Learning in Engineering."
        ),
        "target_module": "Advanced Machine Learning",
        "target_code": "M1552",
    },
]


# ── Quick stats ───────────────────────────────────────────────
if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame(GOLD_STANDARD)
    print(f"Total queries : {len(df)}")
    print("\nBy category:")
    print(df["category"].value_counts().to_string())
    print("\nBy difficulty:")
    print(df["difficulty"].value_counts().to_string())