# User Profile (in latex format)

```latex
\documentclass[10pt]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\usepackage{ragged2e}
\usepackage[english]{babel}
\usepackage{microtype}

% Prevent word breaks
\hyphenpenalty=10000
\exhyphenpenalty=10000

% Remove page numbering
\pagenumbering{gobble}

% Customize section titles with horizontal lines
\titleformat{\section}{\Large\bfseries}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\large\bfseries}{}{0em}{}

% Adjust spacing around titles
\titlespacing*{\section}{0pt}{3pt}{4pt}
\titlespacing*{\subsection}{0pt}{0pt}{0pt}

% Horizontal line style
\renewcommand{\titlerule}{{\vspace{0pt}\hrule}}

% Justify text
\AtBeginDocument{\justifying}

\setlist[itemize]{noitemsep, topsep=0pt}

\begin{document}

% Header
\begin{center}
{\LARGE \textbf{Ricardo Castro Figueiredo}}\\[2pt]
{\small Oliveira de Azeméis, Portugal \quad \textbar \quad +351\,967\,381\,109 \quad \textbar \quad \href{mailto:ricardocastrofigueiredo@gmail.com}{ricardocastrofigueiredo@gmail.com}} \\[4pt]
\href{https://www.linkedin.com/in/ricardo-figueiredo-ba5245235/}{\underline{LinkedIn}}
\quad $\bullet$ \quad
\href{https://github.com/ricardofig016}{\underline{GitHub}}
\quad $\bullet$ \quad
\href{https://ricardofig016.github.io/}{\underline{Portfolio}}
\end{center}

% Remove this when missing space
%\vspace{2pt}
%\hrule
%\vspace{4pt}

% Experience
\section*{Experience}

\subsection*{Skill \& Reach \hfill Porto, Portugal}
\textit{Software Developer – Intern \hfill Oct. 2025 -- Dec. 2025}
\begin{itemize}
\item Built an end-to-end OSINT news ingestion pipeline aggregating RSS feeds and scraped web sources.
\item Applied LLM-based enrichment for article classification, summarization, and criticality scoring, with heuristic fallbacks.
\item Implemented semantic deduplication and related-article linking using vector embeddings and Elasticsearch.
\item Developed a FastAPI backend and React control center for article management and automated email reports.
\end{itemize}

\vspace{4pt}

\subsection*{Critical Manufacturing \hfill Maia, Portugal}
\textit{Software Developer -- Intern \hfill July 2024 -- Sept. 2024}
\begin{itemize}
\item Designed and deployed Feedback Circle, a full-stack web application that streamlined the company's performance appraisal process
\item Implemented a component-based architecture using vanilla JavaScript, HTML, and CSS for the frontend, with Node.js and MySQL for the backend
\item Built a RESTful API handling user authentication, feedback management, and role-based visibility control
\item Created a database schema to manage feedback workflows between employees, managers, and appraisers
\end{itemize}

% Projects
\section*{Projects}
\begin{itemize}
\item \textbf{Kotlin Compiler} \hfill \textit{Haskell, Alex/Happy, MIPS}
\begin{itemize}[leftmargin=*]
\item Developed compiler with lexer/parser (Alex/Happy), semantic checks, and MIPS codegen for Kotlin constructs
\item Optimized via graph coloring register allocation and liveness analysis
\end{itemize}

\item \textbf{CART Class Imbalance} \hfill \textit{Python, scikit-learn, SMOTE}
\begin{itemize}[leftmargin=*]
\item Improved Recall score by 18\% with weighted Gini impurity for minority classes
\item Validated via stratified sampling and ROC-AUC metrics across several datasets
\end{itemize}

% Remove this project when missing space
\item \textbf{Roomba Battle Bot} \hfill \textit{Java, Robocode}
\begin{itemize}[leftmargin=*]
\item Predictive targeting using trigonometry and adaptive bullet power
\item Energy-efficient evasion via collision timeout tracking + zigzag movement
\end{itemize}

\item \textbf{Shinsu Duel: a Tower of God CCG} \hfill \textit{Node.js, Socket.IO, Express}
\begin{itemize}[leftmargin=*]
\item Real-time PvP/PvE card game with synced state management
\item Component-based UI with drag-and-drop interactions
\end{itemize}

\item \textbf{Cryptography Benchmark} \hfill \textit{Python, Cryptography, Matplotlib}
\begin{itemize}[leftmargin=*]
\item Automated performance analysis of AES/RSA/SHA-256
\item Visualized encryption-decryption trends with statistical averaging
\end{itemize}
\end{itemize}

% Education
\section{Education}
\subsection{Bachelor in Computer Science \hfill University of Porto}
\textit{Expected Feb. 2026}
\begin{itemize}
\item \textbf{Relevant Coursework:} Algorithms \& Data Structures, AI/ML, Computer Systems, Databases \& Big Data, Security \& Cryptography, Software Architecture, Mathematics, Programming Paradigms, Theory of Computation, Human-Machine Interaction
\end{itemize}

% Skills
\section*{Skills}
\begin{itemize}
\item \textbf{Languages:} Python, Java, C++, Haskell, SQL, JavaScript, TypeScript, HTML/CSS, Bash/Shell, LaTeX
\item \textbf{Tools \& Frameworks:} Node.js, Express.js, FastAPI, REST APIs, MySQL, MongoDB, Elasticsearch, React, Git, LLMs, Pandas, NumPy, TCP/IP, AMPL, Jupyter
\item \textbf{Platforms:} AWS, GCP, Linux/Unix, Docker
\end{itemize}

% Certifications
\section*{Certifications}
\begin{itemize}
\item English C1 Advanced (CAE), Cambridge Assessment English \hfill \textit{June 2021}
\end{itemize}

\end{document}
```
