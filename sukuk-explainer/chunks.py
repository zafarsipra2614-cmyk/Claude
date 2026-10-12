import json
C=[
"You know how shares work.|But what is a sukuk,|on the Pakistan Stock Exchange?",
"Start with something real.|Say, a stretch of motorway.",
"A sukuk is a certificate|that gives you a share|in owning an asset like this.",
"Every certificate has the same value,|so each one is an equal slice.",
"In Pakistan, government sukuk have used|assets like the M-1 motorway|and Jinnah International Airport.",
"Here's how it works.|Investors pay money,|and the government sells them|a share of the asset.",
"But the government still needs the motorway,|so it leases it back.",
"For using it, the government|pays rent to the sukuk holders.",
"That's the big idea.|Your return is rent from an asset,|not interest on a loan.",
"That's why it's called an Ijarah sukuk.|Ijarah means lease.",
"When the term ends,|after one, three, five or ten years,|the government buys the asset back,",
"and investors get their money back.",
"So where does|the stock exchange come in?",
"Since December 2023,|Government of Pakistan Ijarah Sukuk|have been auctioned through PSX.",
"They come in units of 5,000 rupees,|small enough for a retail investor.",
"Open a brokerage account|and a CDC sub-account,|and you can buy and sell them|like shares.",
"By September 2024,|these PSX auctions had raised|over one trillion rupees.",
"One thing to watch:|sell before maturity,|and the price may be higher|or lower than you paid.",
"So a sukuk is simple.|You own a slice of a real asset,|and it pays you rent.",
]
s=json.load(open('script.json'))
for l,c in zip(s,C):
    if c.replace('|',' ')!=l['sub']: print('MISMATCH',repr(c),repr(l['sub']))
    l['chunks']=c.split('|')
json.dump(s,open('script.json','w'),indent=1,ensure_ascii=False)
