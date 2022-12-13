from discordbot.wordle.wordlesolver import WordleSolver

if __name__ == "__main__":
    answers = []
    for i in range(25):
        solver = WordleSolver()
        answer = solver.solve()
        answers.append(answer)
    print(answers)
