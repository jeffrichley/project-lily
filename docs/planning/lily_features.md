Project Lily

What makes it different from a simple CLI:

Persistent process: Once started, it stays running, so you can keep an ongoing conversation without restarting it every time.

Context retention: Remembers your session history during the run, so it can refer back to earlier questions, code, or files.

Interactive mode: Functions like a REPL (Read–Eval–Print Loop) but with an AI model instead of just a programming language interpreter.

Command execution & integration: Often able to run shell commands, open files, or integrate with local tools while keeping the conversation going.

Lightweight “agent shell”: It’s almost like a minimal TUI (text-based user interface) agent framework embedded in your terminal.



Activities

1. I want to start the application on the command line by typing 'lily'
2. when started, the app will check if the global config is setup in the users home directory at ~/.lily
    - we will have a number of markdown files that are global rules
    - we will have a subdirectory named commands
    - any markdown file in the commands directory becomes a slash command when lily is running
    - when the user types '/' they will get tab completions for the commands in the commands directory
    - when the user selects the slash command they want, it will be executed
    - the markdown files will have instructions and steps that need to be executed by an LLM or scripting environemnt
    - we will need some sort of mechanism to parse the md files to see if scripts would be run or llms
    - instead of having the .md extension, we will use .petal
3. the user should be able to run a petal file directly from outside of a running lily instance by typing 'lily run mytask.petal'
3. when in the application, i also want to be able to have a conversation with an llm agent