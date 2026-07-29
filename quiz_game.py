import json
import random
from datetime import datetime
import os
from quiz import Quiz

class QuizGame:
    def __init__(self, filename="state.json"):
        self.filename = filename
        self.quizzes = []
        self.best_score = 0
        self.history = []
        self.load_state()

    def load_state(self):
        if not os.path.exists(self.filename):
            self.set_default_quizzes()
            self.save_state()
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
                self.best_score = data.get("best_score", 0)
                self.history = data.get("history", [])
        except (json.JSONDecodeError, Exception):
            print("⚠️ 데이터 파일이 손상되었습니다. 기본 데이터로 복구합니다.")
            self.set_default_quizzes()
            self.save_state()

    def save_state(self):
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history": self.history
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def set_default_quizzes(self):
        self.quizzes = [
            Quiz("Python의 창시자는?", ["Guido van Rossum", "Linus Torvalds", "Bjarne Stroustrup", "James Gosling"], 1, "네덜란드 출신 개발자입니다."),
            Quiz("다음 중 Python의 기본 데이터 타입이 아닌 것은?", ["int", "list", "array", "dict"], 3, "표준 라이브러리인 배열 모듈이 따로 있긴 하지만, 기본 타입은 아닙니다."),
            Quiz("Python에서 함수를 정의할 때 사용하는 키워드는?", ["func", "def", "function", "define"], 2, "define의 약자입니다."),
            Quiz("리스트의 마지막 요소를 제거하고 반환하는 메서드는?", ["remove()", "delete()", "pop()", "push()"], 3, "풍선이 터지는 소리를 생각해보세요."),
            Quiz("문자열 길이를 반환하는 내장 함수는?", ["length()", "size()", "len()", "count()"], 3, "length의 앞 3글자입니다.")
        ]
        self.best_score = 0
        self.history = []

    def run(self):
        while True:
            self.show_menu()
            choice = input("👉 메뉴를 선택하세요 (1-6): ").strip()
            if choice == '1': self.play_quiz()
            elif choice == '2': self.add_quiz()
            elif choice == '3': self.show_list()
            elif choice == '4': self.delete_quiz()
            elif choice == '5': self.show_score()
            elif choice == '6':
                print("🚪 게임을 종료합니다. 데이터가 저장되었습니다.")
                self.save_state()
                break
            else:
                print("❌ 올바른 번호를 입력해주세요.")

    def show_menu(self):
        print("\n" + "="*30)
        print("🎯 파이썬 상식 퀴즈 게임 🎯")
        print("="*30)
        print("1. 📝 퀴즈 풀기")
        print("2. ➕ 퀴즈 추가")
        print("3. 📋 퀴즈 목록")
        print("4. 🗑️ 퀴즈 삭제")
        print("5. 🏆 최고 점수 & 기록 확인")
        print("6. 🚪 종료")
        print("="*30)

    def play_quiz(self):
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해주세요.")
            return

        print(f"\n💡 현재 총 {len(self.quizzes)}개의 퀴즈가 있습니다.")
        try:
            num = input("몇 문제를 푸시겠습니까? (전체 풀려면 엔터): ").strip()
            if num == "":
                num_questions = len(self.quizzes)
            else:
                num_questions = int(num)
                if num_questions <= 0 or num_questions > len(self.quizzes):
                    print(f"❌ 1에서 {len(self.quizzes)} 사이의 숫자를 입력해주세요.")
                    return
        except ValueError:
            print("❌ 숫자로 입력해주세요.")
            return

        quiz_pool = random.sample(self.quizzes, num_questions)
        score = 0
        total_points = num_questions * 10
        earned_points = 0

        for i, q in enumerate(quiz_pool, 1):
            print(f"\n[{i}/{num_questions}]")
            q.display()
            
            while True:
                ans = input("👉 정답을 입력하세요 (1-4, 힌트: h): ").strip()
                if ans.lower() == 'h':
                    if q.hint:
                        print(f"💡 힌트: {q.hint}")
                    else:
                        print("💡 힌트가 없는 문제입니다.")
                    continue
                try:
                    ans_int = int(ans)
                    if 1 <= ans_int <= 4:
                        break
                    print("❌ 1~4 사이의 숫자를 입력해주세요.")
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            
            if q.check(ans_int):
                print("✅ 정답입니다!")
                earned_points += 10
                score += 1
            else:
                print(f"❌ 오답입니다. 정답은 {q.answer}번입니다.")
        
        final_score = int((earned_points / total_points) * 100) if total_points > 0 else 0
        print(f"\n🏁 게임 종료! 총 {num_questions}문제 중 {score}문제를 맞혔습니다.")
        print(f"📊 최종 점수: {final_score}점")

        if final_score > self.best_score:
            print("🎉 신기록 달성! 축하합니다! 🎉")
            self.best_score = final_score

        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "solved": num_questions,
            "score": final_score
        })
        self.save_state()

    def add_quiz(self):
        print("\n➕ 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()
        if not question: return
        
        choices = []
        for i in range(1, 5):
            choice = input(f"보기 {i}번을 입력하세요: ").strip()
            choices.append(choice)
        
        while True:
            try:
                answer = int(input("정답 번호 (1-4)를 입력하세요: ").strip())
                if 1 <= answer <= 4:
                    break
                print("❌ 1~4 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        hint = input("힌트를 입력하세요 (없으면 엔터): ").strip()
        
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save_state()
        print("✅ 퀴즈가 성공적으로 추가되었습니다!")

    def show_list(self):
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for i, q in enumerate(self.quizzes, 1):
            print(f"{i}. {q.question}")
            
    def delete_quiz(self):
        self.show_list()
        if not self.quizzes:
            return
        try:
            num = int(input("\n🗑️ 삭제할 퀴즈 번호를 입력하세요 (취소: 0): ").strip())
            if num == 0: return
            if 1 <= num <= len(self.quizzes):
                deleted = self.quizzes.pop(num - 1)
                print(f"✅ '{deleted.question}' 퀴즈가 삭제되었습니다.")
                self.save_state()
            else:
                print("❌ 잘못된 번호입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")

    def show_score(self):
        print("\n🏆 최고 점수 및 기록 확인 🏆")
        print(f"👑 최고 점수: {self.best_score}점")
        if not self.history:
            print("기록이 없습니다. 퀴즈에 도전해보세요!")
        else:
            print("\n📜 최근 플레이 기록:")
            # 최근 5개만 역순으로 출력
            for h in reversed(self.history[-5:]):
                print(f"- {h['date']} | 푼 문제: {h['solved']}개 | 점수: {h['score']}점")
