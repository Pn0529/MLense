# GATE Previous Year Questions organized by topic
# Each question has: question text, 4 options, correct answer index, year, and explanation

GATE_PYQS = {
    "Operating Systems": [
        {
            "question": "Which of the following page replacement algorithms suffers from Belady's anomaly?",
            "options": ["LRU", "Optimal", "FIFO", "LFU"],
            "answer": 2,
            "year": "GATE 2019",
            "explanation": "FIFO page replacement algorithm suffers from Belady's anomaly, where increasing the number of page frames can actually increase the number of page faults."
        },
        {
            "question": "A system has 3 processes sharing 4 instances of a resource. Each process can request a maximum of 2 instances. Which of the following is TRUE?",
            "options": [
                "Deadlock can occur",
                "Deadlock cannot occur",
                "Starvation will always occur",
                "The system will always be in an unsafe state"
            ],
            "answer": 1,
            "year": "GATE 2020",
            "explanation": "With 3 processes each needing at most 2, in the worst case each holds 1 (using 3 total). The remaining 1 instance can satisfy any process, so deadlock cannot occur."
        },
        {
            "question": "Consider a system with 5 processes P0 through P4 and 3 resource types A (10 instances), B (5 instances), C (7 instances). At time T0, the following snapshot is taken. What is the safe sequence?",
            "options": [
                "P1, P3, P4, P2, P0",
                "P0, P1, P2, P3, P4",
                "P4, P3, P2, P1, P0",
                "No safe sequence exists"
            ],
            "answer": 0,
            "year": "GATE 2018",
            "explanation": "Using the Banker's algorithm, P1 can finish first, followed by P3, P4, P2, and finally P0, forming a safe sequence."
        },
        {
            "question": "Which scheduling algorithm gives minimum average waiting time?",
            "options": ["FCFS", "SJF", "Round Robin", "Priority"],
            "answer": 1,
            "year": "GATE 2017",
            "explanation": "Shortest Job First (SJF) scheduling gives the minimum average waiting time among all scheduling algorithms."
        },
        {
            "question": "A counting semaphore S is initialized to 10. Then, 6 P(S) operations and 4 V(S) operations are performed on S. What is the final value of S?",
            "options": ["6", "8", "10", "4"],
            "answer": 1,
            "year": "GATE 2021",
            "explanation": "Initial value = 10. After 6 P operations: 10 - 6 = 4. After 4 V operations: 4 + 4 = 8."
        }
    ],
    "Computer Networks": [
        {
            "question": "In TCP, the sender window size is determined by:",
            "options": [
                "Only receiver window",
                "Only congestion window",
                "Minimum of receiver window and congestion window",
                "Maximum of receiver window and congestion window"
            ],
            "answer": 2,
            "year": "GATE 2020",
            "explanation": "TCP sender window = min(receiver window, congestion window). This ensures flow control and congestion control simultaneously."
        },
        {
            "question": "Which layer of OSI model is responsible for end-to-end delivery of a message?",
            "options": ["Network Layer", "Transport Layer", "Session Layer", "Data Link Layer"],
            "answer": 1,
            "year": "GATE 2019",
            "explanation": "The Transport Layer (Layer 4) is responsible for end-to-end delivery of messages between processes."
        },
        {
            "question": "The minimum number of bits required to represent the number of hosts in a Class B network is:",
            "options": ["8", "14", "16", "24"],
            "answer": 2,
            "year": "GATE 2018",
            "explanation": "A Class B network uses 16 bits for the host part, allowing 2^16 - 2 = 65,534 hosts."
        },
        {
            "question": "What is the maximum data rate of a noiseless channel with bandwidth B and L signal levels, according to Nyquist's theorem?",
            "options": ["B log2 L", "2B log2 L", "B log2 (1 + S/N)", "2B log2 (1 + S/N)"],
            "answer": 1,
            "year": "GATE 2017",
            "explanation": "Nyquist's theorem states: Maximum data rate = 2B log₂(L) bps for a noiseless channel."
        },
        {
            "question": "ARP (Address Resolution Protocol) is used to find:",
            "options": [
                "IP address from MAC address",
                "MAC address from IP address",
                "IP address from domain name",
                "Domain name from IP address"
            ],
            "answer": 1,
            "year": "GATE 2021",
            "explanation": "ARP resolves an IP address to its corresponding MAC (hardware) address on a local network."
        }
    ],
    "Database Management Systems": [
        {
            "question": "A relation R(A, B, C, D) with FD set {A→B, B→C, C→D, D→B}. The candidate key(s) of R is/are:",
            "options": ["A", "AB", "ABC", "ABCD"],
            "answer": 0,
            "year": "GATE 2020",
            "explanation": "From A→B→C→D→B, A can determine all other attributes. So A is the only candidate key."
        },
        {
            "question": "Which normal form is based on the concept of transitive dependency?",
            "options": ["1NF", "2NF", "3NF", "BCNF"],
            "answer": 2,
            "year": "GATE 2019",
            "explanation": "Third Normal Form (3NF) eliminates transitive dependencies, where a non-prime attribute depends on another non-prime attribute."
        },
        {
            "question": "The minimum number of tables required to represent a many-to-many relationship between two entities is:",
            "options": ["1", "2", "3", "4"],
            "answer": 2,
            "year": "GATE 2018",
            "explanation": "A many-to-many relationship requires 3 tables: one for each entity and one junction/bridge table."
        },
        {
            "question": "Which of the following is NOT a property of a transaction (ACID)?",
            "options": ["Atomicity", "Consistency", "Isolation", "Distributivity"],
            "answer": 3,
            "year": "GATE 2017",
            "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability. Distributivity is not a transaction property."
        },
        {
            "question": "In SQL, which command is used to remove all rows from a table without logging individual row deletions?",
            "options": ["DELETE", "DROP", "TRUNCATE", "REMOVE"],
            "answer": 2,
            "year": "GATE 2021",
            "explanation": "TRUNCATE removes all rows quickly without logging individual deletions, unlike DELETE which logs each row removal."
        }
    ],
    "Data Structures and Algorithms": [
        {
            "question": "The worst-case time complexity of QuickSort is:",
            "options": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
            "answer": 1,
            "year": "GATE 2019",
            "explanation": "QuickSort's worst case occurs when the pivot is always the smallest or largest element, leading to O(n²) comparisons."
        },
        {
            "question": "The number of binary trees with 3 nodes that store the keys {1, 2, 3} is:",
            "options": ["3", "4", "5", "6"],
            "answer": 2,
            "year": "GATE 2020",
            "explanation": "The number of structurally distinct BSTs with n nodes is the nth Catalan number. C(3) = 5."
        },
        {
            "question": "Which data structure is used for implementing BFS (Breadth First Search)?",
            "options": ["Stack", "Queue", "Priority Queue", "Linked List"],
            "answer": 1,
            "year": "GATE 2018",
            "explanation": "BFS uses a Queue (FIFO) to explore nodes level by level."
        },
        {
            "question": "The height of a complete binary tree with n nodes is:",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(√n)"],
            "answer": 1,
            "year": "GATE 2017",
            "explanation": "A complete binary tree is balanced, so its height is always O(log n)."
        },
        {
            "question": "What is the recurrence relation for Merge Sort?",
            "options": ["T(n) = T(n-1) + n", "T(n) = 2T(n/2) + n", "T(n) = T(n/2) + 1", "T(n) = 2T(n-1) + 1"],
            "answer": 1,
            "year": "GATE 2021",
            "explanation": "Merge Sort divides the array into 2 halves (2T(n/2)) and merges them in O(n) time, giving T(n) = 2T(n/2) + n."
        }
    ],
    "Digital Logic": [
        {
            "question": "The minimum number of 2-input NAND gates required to implement the Boolean function AB + CD is:",
            "options": ["3", "4", "5", "6"],
            "answer": 0,
            "year": "GATE 2019",
            "explanation": "AB + CD can be implemented using 3 NAND gates: NAND(NAND(A,B), NAND(C,D))."
        },
        {
            "question": "A flip-flop that toggles its output on every clock pulse is:",
            "options": ["SR flip-flop", "D flip-flop", "JK flip-flop with J=K=1", "T flip-flop with T=1"],
            "answer": 3,
            "year": "GATE 2020",
            "explanation": "A T flip-flop with T=1 toggles its output on every clock pulse."
        },
        {
            "question": "How many flip-flops are needed to design a mod-16 counter?",
            "options": ["2", "3", "4", "5"],
            "answer": 2,
            "year": "GATE 2018",
            "explanation": "A mod-16 counter needs log₂(16) = 4 flip-flops to count from 0 to 15."
        },
        {
            "question": "The Boolean expression A + A'B simplifies to:",
            "options": ["A", "B", "A + B", "AB"],
            "answer": 2,
            "year": "GATE 2017",
            "explanation": "A + A'B = A + B (by the absorption law / consensus theorem)."
        },
        {
            "question": "Which of the following is a universal gate?",
            "options": ["AND", "OR", "NAND", "XOR"],
            "answer": 2,
            "year": "GATE 2021",
            "explanation": "NAND and NOR are universal gates because any Boolean function can be implemented using only NAND (or only NOR) gates."
        }
    ],
    "Theory of Computation": [
        {
            "question": "Which of the following languages is NOT context-free?",
            "options": ["a^n b^n", "a^n b^n c^n", "Balanced parentheses", "a^n b^m where n ≤ m"],
            "answer": 1,
            "year": "GATE 2019",
            "explanation": "a^n b^n c^n is a context-sensitive language, not context-free. It cannot be recognized by a pushdown automaton."
        },
        {
            "question": "The complement of a recursive language is:",
            "options": ["Recursive", "Recursively enumerable", "Not recursively enumerable", "Context-free"],
            "answer": 0,
            "year": "GATE 2020",
            "explanation": "Recursive languages are closed under complementation. The complement of a recursive language is also recursive."
        },
        {
            "question": "The minimum number of states in a DFA that accepts strings over {a,b} ending with 'ab' is:",
            "options": ["2", "3", "4", "5"],
            "answer": 1,
            "year": "GATE 2018",
            "explanation": "We need 3 states: start state (no match), state after seeing 'a', and accepting state after seeing 'ab'."
        },
        {
            "question": "Which of the following problems is undecidable?",
            "options": [
                "Whether a CFG generates a specific string",
                "Whether a DFA accepts a given string",
                "Whether two CFGs generate the same language",
                "Whether a string belongs to a regular language"
            ],
            "answer": 2,
            "year": "GATE 2017",
            "explanation": "The equivalence problem for CFGs is undecidable. It cannot be determined algorithmically whether two CFGs generate the same language."
        },
        {
            "question": "A language accepted by a Turing Machine is called:",
            "options": ["Regular", "Context-free", "Context-sensitive", "Recursively enumerable"],
            "answer": 3,
            "year": "GATE 2021",
            "explanation": "Languages accepted by Turing Machines are called recursively enumerable (r.e.) languages."
        }
    ],
    "Probability and Statistics": [
        {
            "question": "If P(A) = 0.3 and P(B) = 0.4, and A and B are independent, then P(A ∩ B) is:",
            "options": ["0.7", "0.12", "0.1", "0.70"],
            "answer": 1,
            "year": "GATE 2020",
            "explanation": "For independent events, P(A ∩ B) = P(A) × P(B) = 0.3 × 0.4 = 0.12."
        },
        {
            "question": "The expected value of a fair die is:",
            "options": ["3", "3.5", "4", "2.5"],
            "answer": 1,
            "year": "GATE 2019",
            "explanation": "E(X) = (1+2+3+4+5+6)/6 = 21/6 = 3.5 for a fair six-sided die."
        },
        {
            "question": "A box contains 4 red and 6 blue balls. Two balls are drawn without replacement. The probability that both are red is:",
            "options": ["2/15", "4/25", "2/5", "1/5"],
            "answer": 0,
            "year": "GATE 2018",
            "explanation": "P(both red) = (4/10) × (3/9) = 12/90 = 2/15."
        },
        {
            "question": "The variance of a constant random variable is:",
            "options": ["1", "The constant itself", "0", "Undefined"],
            "answer": 2,
            "year": "GATE 2017",
            "explanation": "A constant has no variability, so its variance is always 0."
        },
        {
            "question": "In a Poisson distribution with mean λ, the probability of zero occurrences is:",
            "options": ["e^λ", "e^(-λ)", "λ", "1/λ"],
            "answer": 1,
            "year": "GATE 2021",
            "explanation": "P(X=0) = (e^(-λ) × λ^0) / 0! = e^(-λ)."
        }
    ],
    "Compiler Design": [
        {
            "question": "Which of the following is NOT a phase of a compiler?",
            "options": ["Lexical Analysis", "Syntax Analysis", "Resource Allocation", "Code Optimization"],
            "answer": 2,
            "year": "GATE 2019",
            "explanation": "Resource Allocation is not a compiler phase. The phases are: Lexical Analysis, Syntax Analysis, Semantic Analysis, Intermediate Code Generation, Code Optimization, and Code Generation."
        },
        {
            "question": "LALR(1) parsing is a variant of:",
            "options": ["LL parsing", "LR parsing", "Recursive descent parsing", "Operator precedence parsing"],
            "answer": 1,
            "year": "GATE 2020",
            "explanation": "LALR(1) (Look-Ahead LR) is a variant of LR parsing that merges states with the same core items."
        },
        {
            "question": "The token '42' in a programming language is recognized by which phase?",
            "options": ["Syntax Analysis", "Lexical Analysis", "Semantic Analysis", "Code Generation"],
            "answer": 1,
            "year": "GATE 2018",
            "explanation": "Lexical Analysis (scanning) recognizes tokens like numbers, identifiers, and keywords from the source code."
        }
    ]
}

from backend.utils.database import pyqs_collection

def get_pyqs_by_topic(topic_name: str):
    """Find PYQs matching or partially matching a topic name from MongoDB with fallback."""
    topic_lower = topic_name.lower()
    
    # Try fetching from MongoDB first
    if pyqs_collection is not None:
        try:
            # Simple matching for now
            results = list(pyqs_collection.find({}))
            matched = []
            for doc in results:
                cat = doc.get("category", "")
                if (cat.lower() in topic_lower or 
                    topic_lower in cat.lower() or
                    any(keyword in topic_lower for keyword in cat.lower().split())):
                    matched.append({
                        "category": cat,
                        "questions": doc.get("questions", [])
                    })
            if matched:
                return matched
        except Exception as e:
            print(f"Error fetching PYQs from DB: {e}")

    # Fallback to local dictionary
    results = []
    for category, questions in GATE_PYQS.items():
        if (category.lower() in topic_lower or
            topic_lower in category.lower() or
            any(keyword in topic_lower for keyword in category.lower().split())):
            results.append({
                "category": category,
                "questions": questions
            })

    # If no match found, return empty array instead of all categories
    # This prevents showing the same questions for every unrelated topic
    return results

def get_all_categories():
    """Return list of all PYQ categories from MongoDB with fallback."""
    if pyqs_collection is not None:
        try:
            categories = list(pyqs_collection.distinct("category"))
            if categories:
                return categories
        except Exception as e:
            print(f"Error fetching categories from DB: {e}")

    return list(GATE_PYQS.keys())
