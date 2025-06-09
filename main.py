import discord
from discord.ext import commands
import config
import random
import asyncio
import sqlite3
from discord.ext.commands import cooldown, BucketType

import sqlite3



async def fetch_bal(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def update_bal(ctx, new_balance: int):
    user_id = ctx.author.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()

async def get_total_wins(user_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_wins FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def get_total_losses(user_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_losses FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def update_win(ctx):
    user_id = ctx.author.id
    wins = await get_total_wins(user_id) + 1
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET total_wins = ? WHERE user_id = ?", (wins, user_id))
    conn.commit()
    conn.close()

async def update_loss(ctx):
    user_id = ctx.author.id
    losses = await get_total_losses(user_id) + 1
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET total_losses = ? WHERE user_id = ?", (losses, user_id))
    conn.commit()
    conn.close()

async def get_wager(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT wager FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def update_wager(ctx, bet: int):
    user_id = ctx.author.id
    current = await get_wager(ctx) + bet
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET wager = ? WHERE user_id = ?", (current, user_id))
    conn.commit()
    conn.close()

emojis=['✅','❌']
conn =sqlite3.connect("data.db", check_same_thread=False)
cursor=conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 10000,
    wager REAL DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0
)
''')
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS stocks_data(
        name TEXT PRIMARY KEY,
        price REAL
    )'''
)
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS stocks_holdings(
        user_id INTEGER,
        stock_symbol TEXT ,
        quantity INTEGER,
        avg_price REAL,
        PRIMARY KEY(user_id,stock_symbol)
    )'''
)
conn.commit()
conn.close()
def add_user(user_id):
    conn=sqlite3.connect("data.db", check_same_thread=False)
    cursor=conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?",(user_id,))
    result=cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO users (user_id,balance,wager,total_wins,total_losses) VALUES(?,?,?,?,?)",(user_id,10000,0,0,0))
    conn.commit()
    conn.close()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents,help_command=None)

@bot.command()
async def tip(ctx, member: discord.Member, amount: int):
    sender_id = ctx.author.id
    receiver_id = member.id

    # Prevent tipping self
    if sender_id == receiver_id:
        await ctx.send("❌ You can't tip yourself!")
        return

    if amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return

    # Fetch sender balance
    sender_balance = await fetch_bal(ctx)

    if sender_balance < amount:
        await ctx.send("❌ You don't have enough balance to tip.")
        return

    # Deduct from sender
    new_sender_balance = sender_balance - amount
    await update_bal(ctx, new_sender_balance)

    # Fetch receiver balance and update
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (receiver_id,))
    result = cursor.fetchone()
    receiver_balance = result[0] if result else 0
    conn.close()

    await update_bal_member(receiver_id, receiver_balance + amount)

    # Receipt message
    sender_msg = f"💸 You tipped {member.mention} **{amount}** coins.\nNew Balance: **{new_sender_balance}**"
    receiver_msg = f"🎁 You received a tip of **{amount}** coins from {ctx.author.mention}."

    try:
        await ctx.author.send(sender_msg)
    except:
        await ctx.send("⚠️ Couldn't DM the sender.")

    try:
        await member.send(receiver_msg)
    except:
        await ctx.send("⚠️ Couldn't DM the receiver.")

    await ctx.send(f"✅ Successfully tipped **{amount}** coins to {member.mention}!")

# Helper function to update another user's balance (not ctx.author)
async def update_bal_member(user_id, new_balance: int):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
  
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot is online and synced!")
    bot.loop.create_task(pricechange())

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🎮 Available Commands",
        description="Here are all the game and profile commands you can use:",
        color=discord.Color.gold()
    )

    # Balance and Rewards
    embed.add_field(
        name="💰 `.bal`",
        value="Check your current coin balance.",
        inline=False
    )
    embed.add_field(
        name="🎁 `.monthly`",
        value="Claim your monthly reward of 10,000 coins.",
        inline=False
    )
    embed.add_field(
        name="⏳ `.money`",
        value="Claim coins once every hour (random between 250-1000).",
        inline=False
    )

    # Games
    embed.add_field(
        name="🪙 `.coin <0|1> <amount>`",
        value="Flip a coin to double your bet!\n`0` = Heads, `1` = Tails\n💡 Example: `/coin 0 200`",
        inline=False
    )
    embed.add_field(
        name="✈️ `.aero <amount> <multiplier>`",
        value="Play the airplane crash game.\nCash out before it crashes!\n💡 Example: `/aero 200 3.5`",
        inline=False
    )
    embed.add_field(
        name="🪨📄✂️ `.spr <0|1|2> <amount>`",
        value="Rock-Paper-Scissors game!\n`0` = Paper, `1` = Rock, `2` = Scissors\n💡 Example: `/spr 0 100`",
        inline=False
    )
    embed.add_field(
        name="🎲 `.rollover <bet> <rollover>`",
        value="Place a rollover bet.\nTry to beat the bot's roll under the given percentage.\n💡 Example: `/rollover 100 50`",
        inline=False
    )

    # Stocks & Portfolio
    embed.add_field(
        name="📈 `.buy <stock> <quantity>`",
        value="Buy shares of a stock.\n💡 Example: `/buy AAPL 10`",
        inline=False
    )
    embed.add_field(
        name="📉 `.sell <stock> <quantity>`",
        value="Sell shares of a stock you own.\n💡 Example: `/sell AAPL 5`",
        inline=False
    )
    embed.add_field(
        name="📊 `.portfolio`",
        value="View your current stock holdings.",
        inline=False
    )
    embed.add_field(
        name="📝 `.list`",
        value="Get a list of available stocks and their current prices (sent via DM).",
        inline=False
    )

    # Stats and Profile
    embed.add_field(
        name="📊 `.stats`",
        value="View your profile stats including win rate, balance, and more.",
        inline=False
    )
    embed.add_field(
        name="📈 `.wager`",
        value="Check total amount wagered in games.",
        inline=True
    )
    embed.add_field(
        name="✅ `.total_wins`",
        value="View how many times you've won.",
        inline=True
    )
    embed.add_field(
        name="❌ `.total_loss`",
        value="View how many times you've lost.",
        inline=True
    )

    # Leaderboard
    embed.add_field(
        name="🏆 `/leaderboard`",
        value="See the top 3 players by balance.",
        inline=False
    )
    embed.add_field(
    name="💸 `/tip @user amount`",
    value="Tip another user a specific amount of your balance.",
    inline=False
    )
    embed.add_field(
    name="📈 `/stockvalue`",
    value="See the total value of your stock holdings based on live prices.",
    inline=False
    )
    embed.set_footer(text="Use commands wisely and have fun playing! 🎉")

    # Add bot avatar if available
    if ctx.bot.user.avatar:
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def value(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT sh.stock_symbol, sh.quantity, sd.price
        FROM stocks_holdings sh
        JOIN stocks_data sd ON sh.stock_symbol = sd.name
        WHERE sh.user_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await ctx.send("📭 You don't own any stocks.")
        return

    total_value = 0
    embed = discord.Embed(
        title=f"📈 {ctx.author.name}'s Stock Portfolio",
        color=discord.Color.blue()
    )

    for symbol, qty, price in rows:
        value = qty * price
        total_value += value
        embed.add_field(
            name=f"📊 {symbol.upper()}",
            value=f"Qty: {qty} × ₹{price:.2f} = ₹{value:.2f}",
            inline=False
        )

    embed.add_field(
        name="💼 Total Portfolio Value",
        value=f"🪙 ₹{total_value:.2f}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    if hasattr(ctx, "author"):
        user_id = ctx.author.id
    else:
        user_id = ctx.id
    conn = sqlite3.connect("data.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, wager, total_wins, total_losses FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        await ctx.send("❌ You are not registered. Use any game command first to register.")
        return

    balance, wager, total_wins, total_losses = result

    embed = discord.Embed(
        title=f"📊 {ctx.author.name}'s Stats",
        color=discord.Color.purple()
    )

    # Set avatar thumbnail only if the user has one
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)

    embed.add_field(name="💰 Balance", value=f"{balance:.2f} coins", inline=False)
    embed.add_field(name="🎲 Total Wagered", value=f"{wager:.2f} coins", inline=False)
    embed.add_field(name="✅ Total Wins", value=str(total_wins), inline=True)
    embed.add_field(name="❌ Total Losses", value=str(total_losses), inline=True)

    total_games = total_wins + total_losses
    win_rate = f"{(total_wins / total_games) * 100:.2f}%" if total_games > 0 else "N/A"
    embed.add_field(name="📈 Win Rate", value=win_rate, inline=False)

    await ctx.send(embed=embed)



@bot.command()
async def bal(ctx):
    add_user(ctx.author.id)
    result=await fetch_bal(ctx)
    await ctx.send(f"💰 **Your Balance:** `{result:.2f}` coins")

@bot.command()
async def wager(ctx):
    user_id=ctx.author.id
    conn=sqlite3.connect("data.db", check_same_thread=False)
    cursor=conn.cursor()
    cursor.execute("select wager from users where user_id=?",(user_id,))
    result=cursor.fetchone()[0] 
    conn.close()
    await ctx.send(f"✅Total Wager:{result:.2f}")

@bot.command()
async def total_wins(ctx):
    user_id=ctx.author.id
    conn=sqlite3.connect("data.db", check_same_thread=False)
    cursor=conn.cursor()
    cursor.execute("select total_wins from users where user_id=?",(user_id,))
    result=cursor.fetchone()[0] 
    conn.close()
    await ctx.send(f"✅Total Wins:{result}")

@bot.command()
async def leaderboard(ctx):
    conn=sqlite3.connect("data.db", check_same_thread=False)
    cursor=conn.cursor()
    cursor.execute("select user_id,balance from users order by balance desc limit 3")
    result=cursor.fetchall() 
    conn.close()
    embed = discord.Embed(title="🏆 Balance Leaderboard", color=discord.Color.gold())
    for i, (user_id, balance) in enumerate(result, start=1):
        user=await bot.fetch_user(int(user_id))
        embed.add_field(name=f"#{i}: {user.name}", value=f"Balance: 💰 {balance:.2f}", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def total_loss(ctx):
    user_id=ctx.author.id
    conn=sqlite3.connect("data.db", check_same_thread=False)
    cursor=conn.cursor()
    cursor.execute("select total_losses from users where user_id=?",(user_id,))
    result=cursor.fetchone()[0] 
    conn.close()
    await ctx.send(f"❌Total Losses:{result}")

@bot.command()
@cooldown(1, 2592000, BucketType.user) 
async def monthly(ctx):
    add_user(ctx.author.id)
    bal=await fetch_bal(ctx)
    bal+=10000
    await update_bal(ctx,bal)
    await ctx.send(f"Your New Bal :{bal:.2f}")

@bot.command()
async def coin(ctx,user_choice:int,b:int):
    balance=await fetch_bal(ctx)
    c=["Head","Tail"]
    res=""
    if(balance<b):  
        await ctx.send("Insufficient Balanace")
        return 
    await update_wager(ctx,b)
    await ctx.send(f"🪙 Fliping a Coin!!")
    await asyncio.sleep(1)
    newbalance=balance-b
    bot_choice=random.randint(0,1)
    if user_choice==bot_choice:
        winnings=b*2
        newbalance+=winnings
        await update_win(ctx)
        await update_bal(ctx,newbalance)
        res=f"You Won {b*2}"
    else:
        await update_bal(ctx,newbalance)
        await update_loss(ctx)
        res=f"You Loss {b}"
    embed=discord.Embed(
        title="Result",
        description=res,
        color=discord.Color.blue()
    )
    balance=await fetch_bal(ctx)
    embed.add_field(name="👤 Player", value=ctx.author.mention, inline=True)
    embed.add_field(name="🧑 Your Choice", value=c[user_choice], inline=True)
    embed.add_field(name="🤖 Bot's Choice", value=c[bot_choice], inline=True)
    embed.add_field(name="💰 Account Balance", value=balance, inline=True)
    embed.add_field(name="🎲 Your Bet", value=b, inline=True)
    await ctx.send(embed=embed)

def gencrash():
    r=random.random()
    crash=max(1.0, min(1000.0,round(1/(1-r**(1/1.6)),2)))
    return crash

@bot.command()
async def aero(ctx,bal:int,point:float):
    balance=await fetch_bal(ctx)
    if(bal>balance):
        await ctx.send("Insufficient Balanace")
        return 
    newbalance=balance-bal
    crashpoint=gencrash()
    i=1.0
    await update_wager(ctx,bal)
    while i<point:
        if(i>=crashpoint):
            await ctx.send(f"💥Crashed At {i:.2f}.")
            break
        await ctx.send(f"📈 Point At {i:.2f}.Money Cashout {bal*i:.2f}",delete_after=10)
        i+=0.1
        await asyncio.sleep(0.)
    if point<crashpoint:
        winnings=bal*point
        newbalance+=winnings
        await update_bal(ctx,newbalance)
        await update_win(ctx)
    else:
        await update_bal(ctx,newbalance)
        await update_loss(ctx)
    balance=await fetch_bal(ctx)
    embed=discord.Embed(
    title="💲Result",
    description="Aeroplane Crash",
    color=discord.Color.blue()
    )
    embed.add_field(name="👤 Player", value=ctx.author.mention, inline=True)
    embed.add_field(name="🎯 Your Point", value=f"{point:.2f}", inline=True)
    embed.add_field(name="💥 Crash Point", value=f"{crashpoint:.2f}", inline=True)
    embed.add_field(name="💰 Account Balance", value=f"{balance:.2f}", inline=True)
    embed.add_field(name="🎲 Your Bet", value=f"{bal:.2f}", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def spr(ctx,user_choice:int,bal:int):
        balance=await fetch_bal(ctx)
        if(bal>balance):
            await ctx.send("Insufficient Balanace")
            return
        await update_wager(ctx,bal)
        newbalance=balance-bal
        c=["📃","🪨","✂️"]
        bot_choice=random.randint(0,2)
        res=""
        if(bot_choice==user_choice):
            res="Draw!"
        elif user_choice==0 and bot_choice==1:
            res="Won!"
        elif user_choice==1 and bot_choice==2:
            res="Won!"
        elif user_choice==2 and bot_choice==0:
            res="Won!"
        else:
            res="Loss!"
        if(res=="Won!"):
            winnings=bal*3
            newbalance+=winnings
            await update_bal(ctx,newbalance)
            await update_win(ctx)
            await ctx.send(f"You Won 🍺{bal*3}")
        elif(res=="Loss!"):
            await update_bal(ctx,newbalance)
            await update_loss(ctx)
        balance=await fetch_bal(ctx)
        embed=discord.Embed(
        title="Result",
        description=res,
        color=discord.Color.blue()
        )
        embed.add_field(name="👤 Player", value=ctx.author.mention, inline=True)
        embed.add_field(name="🧑 Your Choice", value=c[user_choice], inline=True)
        embed.add_field(name="🤖 Bot's Choice", value=c[bot_choice], inline=True)
        embed.add_field(name="💰 Account Balance", value=balance, inline=True)
        embed.add_field(name="🎲 Your Bet", value=bal, inline=True)
        await ctx.send(embed=embed)

@bot.command()
async def rollover(ctx,bet:int,rollover:float):
    balance=await fetch_bal(ctx)
    if(balance<bet):
        await ctx.send(f"Insufficient Balance")
        return
    if rollover >= 100:
        await ctx.send("Invalid rollover value. Must be less than 100.")
        return
    profit=100/(100-rollover)
    balance-=bet
    guessbybot=random.randint(0,100)
    res=""
    if(guessbybot>rollover):
        newbal=bet*profit
        res="Win"
        await update_bal(ctx,balance+newbal)
        await update_win(ctx)
    else:
        res="Loss"
        await update_bal(ctx,balance)
        await update_loss(ctx)
    embed=discord.Embed(
        title="💲Result",
        description=res,
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Player", value=ctx.author.mention, inline=True)
    embed.add_field(name="💰 Account Balance", value=f"{balance:.2f}", inline=True)
    embed.add_field(name="🎲 Your Bet", value=bet, inline=True)
    embed.add_field(name="🎯 Bot Roll", value=guessbybot, inline=True)
    await ctx.send(embed=embed)

@bot.command()
@cooldown(5, 3600, BucketType.user)
async def money(ctx):
    bal=await fetch_bal(ctx)
    guess=random.randint(250,1000)
    bal+=guess
    await update_bal(ctx,bal)
    await ctx.send(f"💰 You get :{guess:.2f}")

async def fetch_stock(ctx,name1:str):
    name1upper=name1.upper()
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute('SELECT price FROM stocks_data WHERE name=?',(name1upper,))
    result=cursor.fetchone()[0]
    conn.close()
    return result

@bot.command()
async def buy(ctx,name:str,qty:int):
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
    balance=cursor.fetchone()[0]
    cursor.execute('SELECT price FROM stocks_data WHERE name=?',(name.upper(),))
    price=cursor.fetchone()[0]
    totalcost=qty*price
    if totalcost>await fetch_bal(ctx):
        await ctx.send("Insufficient Bal")
        return
    cursor.execute('SELECT quantity,avg_price FROM stocks_holdings WHERE user_id=? AND stock_symbol=?',(ctx.author.id,name.upper(),))
    result1=cursor.fetchone()
    if result1:
        old_qty,old_avg_price=result1
        new_qty=old_qty+qty
        new_avg_price=((old_qty*old_avg_price)+(qty*price))/new_qty
        cursor.execute('UPDATE stocks_holdings SET quantity=?,avg_price=? WHERE user_id=? AND stock_symbol=?',(new_qty,new_avg_price,ctx.author.id,name.upper()))
    else:
        cursor.execute('INSERT INTO stocks_holdings (user_id,stock_symbol,quantity,avg_price) VALUES(?,?,?,?)',(ctx.author.id,name.upper(),qty,price))
    new_bal=balance
    new_bal-=totalcost
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal,ctx.author.id))
    conn.commit()
    conn.close()
    await ctx.author.send(f"✅ Bought {qty} shares of `{name}` at ₹{price:.2f} each.\n🧾 Total Cost: ₹{totalcost:.2f}\n💰 New Balance: ₹{new_bal:.2f}")

@bot.command()
async def portfolio(ctx):
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute("SELECT stock_symbol,quantity FROM stocks_holdings WHERE user_id=?",(ctx.author.id,))
    result=cursor.fetchall()
    message=f"📊 {ctx.author.mention}\n"
    for stock,qty in result:
        message+=f"🔹Stock:{stock} 🔹QTY :{qty}\n"
    conn.close()
    await ctx.send(message)

async def updatestock(item:str,bal:int):
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE stocks_data SET price=? WHERE name=?",(bal,item))
    conn.commit()
    conn.close()


async def pricechange():
    while True:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM stocks_data")
        rows = cursor.fetchall()
        for symbol, current_price in rows:
            change = random.uniform(-0.10, 0.10)
            new_price = round(current_price * (1 + change), 2)
            new_price = max(0.01, new_price)
            cursor.execute("UPDATE stocks_data SET price = ? WHERE name = ?", (new_price, symbol))
        conn.commit()
        conn.close()
        await asyncio.sleep(600)
@bot.command()
async def sell(ctx,name:str,qty:int):
    symbol = name.upper().strip()
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute('SELECT quantity FROM stocks_holdings WHERE user_id=? AND stock_symbol=?',(ctx.author.id,name.upper(),))
    quantity_user=cursor.fetchone()[0]
    cursor.execute('SELECT price FROM stocks_data WHERE name=?',(name.upper(),))
    selling_price=cursor.fetchone()[0]
    if qty>quantity_user:
        await ctx.send("Not Enough Stocks!")
        conn.close()
        return
    updated_quantity=quantity_user-qty
    if updated_quantity==0:
        cursor.execute("DELETE FROM stocks_holdings WHERE user_id = ? AND stock_symbol = ?", (ctx.author.id, symbol))
    else:
        cursor.execute("UPDATE stocks_holdings SET quantity=? WHERE user_id = ? AND stock_symbol = ?",(updated_quantity,ctx.author.id,name.upper()))
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
    balance=cursor.fetchone()[0]
    new_balance=balance+(selling_price*qty)
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance,ctx.author.id))
    conn.commit()
    conn.close()
    await ctx.send(f"✅ You sold `{qty}` shares of `{name}` at ₹{selling_price} each. Total earned: ₹{selling_price * qty}")
@bot.command()
async def list(ctx):
    conn=sqlite3.connect("data.db")
    cursor=conn.cursor()
    cursor.execute("SELECT name,price FROM stocks_data")
    result=cursor.fetchall()
    conn.close()
    message=""
    for name1, price in result:
        message+=f"📊 **{name1}** — 💲{price}\n"
    await ctx.author.send(message,delete_after=120)

async def delete_stock(ctx, symbol: str, qty: int):
    user_id = ctx.author.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM stocks_holdings WHERE user_id = ? AND stock_symbol = ? AND quantity = ?", (user_id, symbol, qty))
    conn.commit()
    conn.close()

    await ctx.send(f"🗑️ Deleted `{symbol}` with quantity `{qty}` for <@{user_id}>.")

    

bot.run(config.DISCORD_TOKEN)
