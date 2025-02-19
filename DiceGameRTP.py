import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import time
import requests
from io import BytesIO

# Valid dice image URLs
DICE_IMAGE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/2/2c/Alea_1.png",
    "https://upload.wikimedia.org/wikipedia/commons/b/b8/Alea_2.png",
    "https://upload.wikimedia.org/wikipedia/commons/2/2f/Alea_3.png",
    "https://upload.wikimedia.org/wikipedia/commons/8/8d/Alea_4.png",
    "https://upload.wikimedia.org/wikipedia/commons/5/55/Alea_5.png",
    "https://upload.wikimedia.org/wikipedia/commons/f/f4/Alea_6.png"
]

class DiceGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Casino Dice Game")
        self.root.geometry("800x600")
        self.root.configure(bg="darkgreen")
        self.root.config(cursor="tcross")

        self.saldo = 50000
        self.bet_options = [1000, 2000, 5000, 10000]
        self.auto_roll = False
        
        tk.Label(root, text="🎲 Casino Dice Game 🎲", font=("Arial", 24, "bold"), bg="darkgreen", fg="gold").pack()
        self.balance_label = tk.Label(root, text=f"Balance: Rp{self.saldo}", font=("Arial", 16, "bold"), bg="darkgreen", fg="white")
        self.balance_label.pack()
        
        tk.Button(root, text="Deposit", font=("Arial", 14), command=self.deposit_money, bg="gold").pack()
        
        tk.Label(root, text="Choose your bet:", font=("Arial", 14), bg="darkgreen", fg="white").pack()
        self.bet_var = tk.IntVar(value=self.bet_options[0])
        for bet in self.bet_options:
            tk.Radiobutton(root, text=f"Rp{bet}", variable=self.bet_var, value=bet, font=("Arial", 12), bg="darkgreen", fg="white").pack()
        
        tk.Label(root, text="Guess the dice roll (1-6):", font=("Arial", 14), bg="darkgreen", fg="white").pack()
        self.guess_entry = tk.Entry(root, font=("Arial", 14))
        self.guess_entry.pack()
        
        self.dice_canvas = tk.Canvas(root, width=120, height=120, bg="darkgreen", highlightthickness=0)
        self.dice_canvas.pack()
        
        # Load dice images from URL
        self.dice_images = []
        for url in DICE_IMAGE_URLS:
            try:
                response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                response.raise_for_status()
                img = Image.open(BytesIO(response.content)).convert("RGBA").resize((120, 120), Image.LANCZOS)
                self.dice_images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"Failed to load image {url}: {e}")
                self.dice_images.append(None)  # Append None if image fails
        
        self.dice_display = self.dice_canvas.create_image(60, 60, image=self.dice_images[0], tags="dice")
        
        self.play_button = tk.Button(root, text="Roll Dice", font=("Arial", 16), command=self.play_game, bg="red", fg="white")
        self.play_button.pack()
        
        self.auto_roll_button = tk.Button(root, text="Auto Roll", font=("Arial", 16), command=self.auto_roll_dice_options, bg="blue", fg="white")
        self.auto_roll_button.pack()
    
    def deposit_money(self):
        amount = simpledialog.askinteger("Deposit", "Enter amount to deposit:", minvalue=1000)
        if amount:
            self.saldo += amount
            self.balance_label.config(text=f"Balance: Rp{self.saldo}")
            self.play_button.config(state=tk.NORMAL)
            messagebox.showinfo("Deposit Successful", f"You have added Rp{amount} to your balance.")
    
    def animate_dice_roll(self, dice_result):
        if 1 <= dice_result <= 6:
            for _ in range(10):
                temp_result = random.randint(1, 6)
                if self.dice_images[temp_result - 1]:
                    self.dice_canvas.itemconfig(self.dice_display, image=self.dice_images[temp_result - 1])
                self.root.update()
                time.sleep(0.1)
            if self.dice_images[dice_result - 1]:
                self.dice_canvas.itemconfig(self.dice_display, image=self.dice_images[dice_result - 1])
    
    def play_game(self):
        bet = self.bet_var.get()
        if bet > self.saldo:
            messagebox.showerror("Error", "Insufficient balance.")
            return
        
        self.saldo -= bet
        self.balance_label.config(text=f"Balance: Rp{self.saldo}")
        
        dice_roll = random.randint(1, 6)
        self.animate_dice_roll(dice_roll)
        
        user_guess = int(self.guess_entry.get())
        if user_guess == dice_roll:
            win_amount = bet * 6
            self.saldo += win_amount
            messagebox.showinfo("Result", f"Dice rolled: {dice_roll}\nYou won Rp{win_amount}!")
        else:
            messagebox.showinfo("Result", f"Dice rolled: {dice_roll}\nYou lost Rp{bet}.")
        
        self.balance_label.config(text=f"Balance: Rp{self.saldo}")
    
    def auto_roll_dice_options(self):
        auto_bet = simpledialog.askinteger("Auto Roll", "Enter bet amount per roll:", minvalue=1000)
        auto_guess = simpledialog.askinteger("Auto Roll", "Enter your dice guess (1-6):", minvalue=1, maxvalue=6)
        if auto_bet and auto_guess:
            while self.saldo >= auto_bet:
                self.bet_var.set(auto_bet)
                self.guess_entry.delete(0, tk.END)
                self.guess_entry.insert(0, str(auto_guess))
                self.play_game()
                self.root.update()
                time.sleep(1)
            messagebox.showinfo("Auto Roll Stopped", "Balance depleted. Stopping auto roll.")
            self.auto_roll_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceGameUI(root)
    root.mainloop()
