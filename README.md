# Gamezo Discord Bot

Gamezo is a multi-game Discord bot featuring gambling games and a virtual stock market. It offers an engaging economy system where users can bet, trade stocks, and compete with others.

## Available Commands

### Balance and Rewards

- `💰 .bal`  
  Check your current coin balance.

- `🎁 .monthly`  
  Claim your monthly reward of 10,000 coins.

- `⏳ .money`  
  Claim coins once every hour (random between 250-1000).

### Games

- `🪙 .coin <0|1> <amount>`  
  Flip a coin to double your bet!  
  `0` = Heads, `1` = Tails  
  Example: `.coin 0 200`

- `✈️ .aero <amount> <multiplier>`  
  Play the airplane crash game. Cash out before it crashes!  
  Example: `.aero 200 3.5`

- `🪨📄✂️ .spr <0|1|2> <amount>`  
  Rock-Paper-Scissors game!  
  `0` = Paper, `1` = Rock, `2` = Scissors  
  Example: `.spr 0 100`

- `🎲 .rollover <bet> <rollover>`  
  Place a rollover bet. Try to beat the bot's roll under the given percentage.  
  Example: `.rollover 100 50`

### Stocks & Portfolio

- `📈 .buy <stock> <quantity>`  
  Buy shares of a stock.  
  Example: `.buy AAPL 10`

- `📉 .sell <stock> <quantity>`  
  Sell shares of a stock you own.  
  Example: `.sell AAPL 5`

- `📊 .portfolio`  
  View your current stock holdings.

- `📝 .list`  
  Get a list of available stocks and their current prices (sent via DM).

### Stats and Profile

- `📊 .stats`  
  View your profile stats including win rate, balance, and more.

- `📈 .wager`  
  Check total amount wagered in games.

- `✅ .total_wins`  
  View how many times you've won.

- `❌ .total_loss`  
  View how many times you've lost.

### Leaderboard & Tips

- `🏆 .leaderboard`  
  See the top 3 players by balance.

- `💸 .tip @user <amount>`  
  Tip another user a specific amount of your balance.

- `📈 .stockvalue`  
  See the total value of your stock holdings based on live prices.

---

## How to Use

- All commands start with the `.` prefix.  
- Use these commands in any Discord server channel where Gamezo is active.  

## Installation & Setup

1. Clone this repo:  
   ```bash
   git clone https://github.com/armanphaugat/gamezo.git
