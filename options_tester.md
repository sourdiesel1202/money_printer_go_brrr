Loading config file for options_tester
## Testing SHORT positions


#### TESTING POSITION 1/5 (ENTRY)
 In order to enter a SHORT position (PUT) in $(F) at bid price with goal ASSET_SET_PRICE of $15.05 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 15.04
asset_change: 0.06
asset_percentage_change: 0.4
bid: 0.36
ask: 0.39
greeks: {'delta': -0.4700047124101207, 'theta': -0.01547070416850569, 'gamma': 0.4649728827864585, 'vega': 0.010386708432297337, 'implied_violatility': 32.7683687210083}
```


#### TESTING POSITION 1/5(EXIT)
 In order to exit a SHORT position (PUT) in $(F) at bid price with goal ASSET_SET_PRICE of $14.82 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.82
asset_change: -0.16
asset_percentage_change: -1.07
bid: 0.39
ask: 0.47
greeks: {'delta': -0.5325491744903564, 'theta': -0.02514211157523686, 'gamma': 0.28582373787022064, 'vega': 0.010229619412039613, 'implied_violatility': 54.07106876373291}
```


#### TESTING POSITION 2/5 (ENTRY)
 In order to enter a SHORT position (PUT) in $(F) at bid price with goal ASSET_PERCENTAGE of 0.6% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

0.6 percent of $14.98: $0.08988
```
asset_price: 15.06
asset_change: 0.08
asset_percentage_change: 0.53
bid: 0.35
ask: 0.39
greeks: {'delta': -0.4596478395639391, 'theta': -0.014549801653071676, 'gamma': 0.4921323774108526, 'vega': 0.010376615589126045, 'implied_violatility': 30.847787857055664}
```


#### TESTING POSITION 2/5(EXIT)
 In order to exit a SHORT position (PUT) in $(F) at bid price with goal ASSET_PERCENTAGE of 0.8% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

0.8 percent of $14.98: $0.11984
```
asset_price: 14.86
asset_change: -0.12
asset_percentage_change: -0.8
bid: 0.39
ask: 0.45
greeks: {'delta': -0.525567561900108, 'theta': -0.023418893093551173, 'gamma': 0.30764145306087953, 'vega': 0.01027036005443121, 'implied_violatility': 50.16529560089111}
```


#### TESTING POSITION 3/5 (ENTRY)
 In order to enter a SHORT position (PUT) in $(F) at bid price with goal OPTION_SET_PRICE of $0.35 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 15.06
asset_change: 0.08
asset_percentage_change: 0.53
bid: 0.35
ask: 0.39
greeks: {'delta': -0.45962350266123736, 'theta': -0.014531072172559027, 'gamma': 0.4927605750510875, 'vega': 0.01037655110231925, 'implied_violatility': 30.80826997756958}
```


#### TESTING POSITION 3/5(EXIT)
 In order to exit a SHORT position (PUT) in $(F) at bid price with goal OPTION_SET_PRICE of $0.45 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.86
asset_change: -0.12
asset_percentage_change: -0.8
bid: 0.39
ask: 0.45
greeks: {'delta': -0.5256030566114234, 'theta': -0.023404957724889132, 'gamma': 0.3078211009767406, 'vega': 0.010270301290477114, 'implied_violatility': 50.13573169708252}
```


#### TESTING POSITION 4/5 (ENTRY)
 In order to enter a SHORT position (PUT) in $(F) at bid price with goal OPTION_TICK of $0.05 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 15.08
asset_change: 0.1
asset_percentage_change: 0.67
bid: 0.34
ask: 0.39
greeks: {'delta': -0.44781585156900194, 'theta': -0.013589404352283996, 'gamma': 0.5232671024738367, 'vega': 0.010354390001262122, 'implied_violatility': 28.873443603515625}
```


#### TESTING POSITION 4/5(EXIT)
 In order to exit a SHORT position (PUT) in $(F) at bid price with goal OPTION_TICK of $0.15 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.98
asset_change: 0.0
asset_percentage_change: 0.0
bid: 0.39
ask: 0.24
greeks: {'delta': -0.4948621854830218, 'theta': -0.01795881768050738, 'gamma': 0.40276124447748024, 'vega': 0.010373749864268469, 'implied_violatility': 38.0859375}
```


#### TESTING POSITION 5/5 (ENTRY)
 In order to enter a SHORT position (PUT) in $(F) at bid price with goal OPTION_PERCENTAGE of 10% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

10 percent of $15 SHORT Option priced at $0.39: $0.03900000000000001
```
asset_price: 15.06
asset_change: 0.08
asset_percentage_change: 0.53
bid: 0.35
ask: 0.39
greeks: {'delta': -0.45962350266123736, 'theta': -0.014531072172559027, 'gamma': 0.4927605750510875, 'vega': 0.01037655110231925, 'implied_violatility': 30.80826997756958}
```


#### TESTING POSITION 5/5(EXIT)
 In order to exit a SHORT position (PUT) in $(F) at bid price with goal OPTION_PERCENTAGE of 15% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

15 percent of $15 SHORT Option priced at $0.39: $0.058499999999999996
```
asset_price: 14.98
asset_change: 0.0
asset_percentage_change: 0.0
bid: 0.39
ask: 0.33
greeks: {'delta': -0.4948621854830218, 'theta': -0.01795881768050738, 'gamma': 0.40276124447748024, 'vega': 0.010373749864268469, 'implied_violatility': 38.0859375}
```

## Testing LONG positions


#### TESTING POSITION 1/5 (ENTRY)
 In order to enter a LONG position (CALL) in $(F) at bid price with goal ASSET_SET_PRICE of $14.88 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.88
asset_change: -0.1
asset_percentage_change: -0.67
bid: 0.34
ask: 0.39
greeks: {'delta': 0.46550859189932287, 'theta': -0.01798965585703377, 'gamma': 0.39913535634153535, 'vega': 0.010266814370134296, 'implied_violatility': 38.54870796203613}
```


#### TESTING POSITION 1/5(EXIT)
 In order to exit a LONG position (CALL) in $(F) at bid price with goal ASSET_SET_PRICE of $15.09 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 15.09
asset_change: 0.11
asset_percentage_change: 0.73
bid: 0.39
ask: 0.45
greeks: {'delta': 0.5488864226924064, 'theta': -0.01817517947413471, 'gamma': 0.39207079111881016, 'vega': 0.010372228819376219, 'implied_violatility': 38.55043649673462}
```


#### TESTING POSITION 2/5 (ENTRY)
 In order to enter a LONG position (CALL) in $(F) at bid price with goal ASSET_PERCENTAGE of 0.6% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

0.6 percent of $14.98: $0.08988
```
asset_price: 14.9
asset_change: -0.08
asset_percentage_change: -0.53
bid: 0.35
ask: 0.39
greeks: {'delta': 0.4734923370546176, 'theta': -0.01804152685385441, 'gamma': 0.39921234220477636, 'vega': 0.010296417487602669, 'implied_violatility': 38.54870796203613}
```


#### TESTING POSITION 2/5(EXIT)
 In order to exit a LONG position (CALL) in $(F) at bid price with goal ASSET_PERCENTAGE of 0.8% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

0.8 percent of $14.98: $0.11984
```
asset_price: 15.1
asset_change: 0.12
asset_percentage_change: 0.8
bid: 0.39
ask: 0.45
greeks: {'delta': 0.5528021384354803, 'theta': -0.018165108834009312, 'gamma': 0.39129719903422716, 'vega': 0.01036598484937695, 'implied_violatility': 38.552284240722656}
```


#### TESTING POSITION 3/5 (ENTRY)
 In order to enter a LONG position (CALL) in $(F) at bid price with goal OPTION_SET_PRICE of $0.35 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.9
asset_change: -0.08
asset_percentage_change: -0.53
bid: 0.35
ask: 0.39
greeks: {'delta': 0.4734448429119069, 'theta': -0.018025259770246344, 'gamma': 0.3995662697674073, 'vega': 0.010296335726448991, 'implied_violatility': 38.51425647735596}
```


#### TESTING POSITION 3/5(EXIT)
 In order to exit a LONG position (CALL) in $(F) at bid price with goal OPTION_SET_PRICE of $0.45 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 15.1
asset_change: 0.12
asset_percentage_change: 0.8
bid: 0.39
ask: 0.45
greeks: {'delta': 0.5528331785074418, 'theta': -0.018143294599245127, 'gamma': 0.39175950099525014, 'vega': 0.010365876807191178, 'implied_violatility': 38.506388664245605}
```


#### TESTING POSITION 4/5 (ENTRY)
 In order to enter a LONG position (CALL) in $(F) at bid price with goal OPTION_TICK of $0.05 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.88
asset_change: -0.1
asset_percentage_change: -0.67
bid: 0.34
ask: 0.39
greeks: {'delta': 0.4654478004516084, 'theta': -0.017971504252642354, 'gamma': 0.3995279021917668, 'vega': 0.010266678312840484, 'implied_violatility': 38.51032257080078}
```


#### TESTING POSITION 4/5(EXIT)
 In order to exit a LONG position (CALL) in $(F) at bid price with goal OPTION_TICK of $0.15 (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

```
asset_price: 14.98
asset_change: 0.0
asset_percentage_change: 0.0
bid: 0.39
ask: 0.24
greeks: {'delta': 0.5051378145169781, 'theta': -0.01795881768050738, 'gamma': 0.40276124447748024, 'vega': 0.010373749864268469, 'implied_violatility': 38.0859375}
```


#### TESTING POSITION 5/5 (ENTRY)
 In order to enter a LONG position (CALL) in $(F) at bid price with goal OPTION_PERCENTAGE of 10% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

10 percent of $15 LONG Option priced at $0.39: $0.03900000000000001
```
asset_price: 14.9
asset_change: -0.08
asset_percentage_change: -0.53
bid: 0.35
ask: 0.39
greeks: {'delta': 0.4734448429119069, 'theta': -0.018025259770246344, 'gamma': 0.3995662697674073, 'vega': 0.010296335726448991, 'implied_violatility': 38.51425647735596}
```


#### TESTING POSITION 5/5(EXIT)
 In order to exit a LONG position (CALL) in $(F) at bid price with goal OPTION_PERCENTAGE of 15% (current ask: 0.39, current asset price: 14.98), the following price change needs to occur

15 percent of $15 LONG Option priced at $0.39: $0.058499999999999996
```
asset_price: 14.98
asset_change: 0.0
asset_percentage_change: 0.0
bid: 0.39
ask: 0.33
greeks: {'delta': 0.5051378145169781, 'theta': -0.01795881768050738, 'gamma': 0.40276124447748024, 'vega': 0.010373749864268469, 'implied_violatility': 38.0859375}
```


Completed testing  of (F) CALL in 0 minutes and 1 seconds
