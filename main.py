import os
import json

key = open('api-key').read()
symbol = "QQQ"
portSize = 500000
output = open("{}-table.html".format(symbol), "w")

r = json.loads(os.popen('curl -X GET --header "Authorization: " "https://api.tdameritrade.com/v1/marketdata/chains?apikey={}&symbol={}&contractType=ALL&includeQuotes=TRUE&strategy=ANALYTICAL"'.format(key, symbol)).read())

output.write("""<table style="width:100%">
                    <tr>
                        <th>Date</th>
                        <th>Short Strike</th>
                        <th>Long Strike</th>
                        <th>Spreads Sold</th>
                        <th>Margin Required</th>
                        <th>Max Gain</th>
                        <th>Max Loss</th>
                        <th>RR</th>
                    </tr>""")

for exp in r['putExpDateMap'].keys():
        for strike in r['putExpDateMap'][exp]:
            if float(strike) < float(r['underlying']['mark']) and r['putExpDateMap'][exp][strike][0]['bid'] > 0: # if OTM and liquid
                shortStrike = float(strike)
                shortBid = float(r['putExpDateMap'][exp][strike][0]['bid'])
                shortAsk = float(r['putExpDateMap'][exp][strike][0]['ask'])
            
                longStrike = list(r['putExpDateMap'][exp].keys())[list(r['putExpDateMap'][exp].keys()).index(strike) - 1]
                longBid = r['putExpDateMap'][exp][longStrike][0]['bid']
                longAsk = r['putExpDateMap'][exp][longStrike][0]['ask']

                margin = 100 * ((float(shortStrike) - float(longStrike)) + (longAsk))
                spreads = round(portSize / margin)

                maxLoss = spreads * 100 * ( ((float(shortStrike) - float(longStrike)) - (shortBid - longAsk))) # something is wrong here...
                maxGain = spreads * (100 * (shortBid - longAsk))
                rr = maxGain / maxLoss
                if maxGain < 0.0: continue

                """
                    the amount by which the long put aggregate strike price is below the short put aggregate strike price (aggregate strike price = number of contracts x strike price x $100)
                    long put(s) must be paid for in full
                    proceeds received from sale of short put(s) may be applied to the initial margin requirement
                    the short put(s) may expire before the long put(s) and not affect margin requirement
                """
         
                output.write("""
                        <tr>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                        """.format(exp, shortStrike, longStrike, spreads, margin, maxGain, maxLoss, rr))

output.write("</table>")
                                        


