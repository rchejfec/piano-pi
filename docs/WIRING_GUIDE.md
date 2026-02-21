# 🔌 Wiring Guide — Piano Pi Brain

Complete beginner guide. Do this with the Pi **powered off**.

## What You Need From Your Kit

Grab these from your Arduino UNO R3 starter kit:

- **3 push buttons** (small, 4-pin tactile switches)
- **3 LEDs** — 1 green, 1 yellow, 1 red
- **3 resistors** — 220Ω or 330Ω (for LEDs). They have color bands: red-red-brown (220Ω) or orange-orange-brown (330Ω)
- **~12 jumper wires** (male-to-male or male-to-female, depending on your kit)
- **1 breadboard**

---

## Breadboard Basics (30 seconds)

```
         Breadboard Layout
    ┌─────────────────────────────┐
    │  + + + + + + + + + + + + +  │  ← Power rail (all connected horizontally)
    │  - - - - - - - - - - - - -  │  ← Ground rail (all connected horizontally)
    │                             │
    │  a b c d e     f g h i j    │
    │  ┊ ┊ ┊ ┊ ┊     ┊ ┊ ┊ ┊ ┊   │
    │ 1○─○─○─○─○     ○─○─○─○─○ 1 │  ← Row 1: a-e connected, f-j connected
    │ 2○─○─○─○─○     ○─○─○─○─○ 2 │  ← Row 2: same idea
    │ 3○─○─○─○─○     ○─○─○─○─○ 3 │
    │   ... (rows continue) ...   │
    │                             │
    │  - - - - - - - - - - - - -  │
    │  + + + + + + + + + + + + +  │
    └─────────────────────────────┘
```

**Key rule**: In each row, holes a–e are connected. Holes f–j are connected. The gap in the middle separates them.

---

## Pi GPIO Pin Map

Looking at the Pi with the USB ports on the bottom:

```
                    ┌──────────┐
             3V3  1 │ ●  ●  │ 2   5V
    (SDA)  GPIO2  3 │ ●  ●  │ 4   5V
    (SCL)  GPIO3  5 │ ●  ●  │ 6   GND ←──── USE THIS
           GPIO4  7 │ ●  ●  │ 8   GPIO14
             GND  9 │ ●  ●  │ 10  GPIO15
   BTN1 → GPIO17 11 │ ●  ●  │ 12  GPIO18 ← GREEN LED
   BTN3 → GPIO27 13 │ ●  ●  │ 14  GND
   BTN2 → GPIO22 15 │ ●  ●  │ 16  GPIO23 ← YELLOW LED
             3V3 17 │ ●  ●  │ 18  GPIO24 ← RED LED
          GPIO10 19 │ ●  ●  │ 20  GND
           GPIO9 21 │ ●  ●  │ 22  GPIO25
          GPIO11 23 │ ●  ●  │ 24  GPIO8
             GND 25 │ ●  ●  │ 26  GPIO7
              ...   │      │
                    └──────────┘
                    (USB ports)
```

You only need **7 pins**: GPIO 17, 27, 22 (buttons), GPIO 18, 23, 24 (LEDs), and GND.

---

## Step 1: Connect Ground

First, connect the Pi's ground to the breadboard's ground rail.

```
    Pi Pin 6 (GND) ────wire────→ Breadboard "-" rail (blue line)
```

This shares ground with all buttons and LEDs.

---

## Step 2: Wire the 3 Buttons

Each button connects between a GPIO pin and ground. That's it — 2 wires per button.

**How the button works:**
```
    Button has 4 pins in a square:
    ┌───┐
    │ A─┼─B │   A-B are always connected
    │   │   │   C-D are always connected
    │ C─┼─D │   Press button → A connects to C
    └───┘
```

Place each button **straddling the center gap** of the breadboard:

```
    BUTTON 1 (Restart/Shutdown — GPIO 17)
    ═══════════════════════════════════════

    Breadboard:
              a   b   c   d   e       f   g   h   i   j
         ┌────────────────────────────────────────────┐
    row5 │    ○   ○  [BTN]  ○       ○  [BTN]  ○   ○  │
    row6 │    ○   ○  [BTN]  ○       ○  [BTN]  ○   ○  │
         └────────────────────────────────────────────┘

    Wire 1: Pi GPIO 17 (pin 11) ───→ row 5, column a
    Wire 2: Breadboard "-" rail ───→ row 6, column a

    That's it! When you press the button, GPIO 17 connects to GND.
```

**Repeat for the other 2 buttons** in different rows:

```
    BUTTON 2 (Next instrument — GPIO 27)
    Wire 1: Pi GPIO 27 (pin 13) ───→ row 8, column a
    Wire 2: Breadboard "-" rail ───→ row 9, column a
    Button: straddles rows 8-9 across the center gap

    BUTTON 3 (Previous instrument — GPIO 22)
    Wire 1: Pi GPIO 22 (pin 15) ───→ row 11, column a
    Wire 2: Breadboard "-" rail ───→ row 12, column a
    Button: straddles rows 11-12 across the center gap
```

---

## Step 3: Wire the 3 LEDs

Each LED needs a **resistor** to avoid burning out. The circuit is:

```
    GPIO pin ──→ Resistor (220Ω) ──→ LED long leg (+) ──→ LED short leg (-) ──→ GND
```

**LED legs**: The **longer leg is positive** (+, anode). The **shorter leg is negative** (-, cathode).

```
    GREEN LED (Ready — GPIO 18)
    ════════════════════════════

    Breadboard row 16-18:

              a   b   c   d   e
         ┌──────────────────────────┐
   row16 │  ○   ○   ○   ○   ○      │ ← GPIO 18 wire goes here (col a)
   row17 │  ○  [===RESISTOR===]  ○  │ ← Resistor from col a (row16) to col d (row16)
         │                          │   Actually: put resistor legs in row16-col-a
   row18 │  ○   ○   ○   ○   ○      │   and row16-col-d
         └──────────────────────────┘

    Simplified wiring — do this for each LED:

    1. Resistor: one leg in row 16 col a, other leg in row 16 col d
    2. LED long leg (+): row 16 col e (connects to resistor via row)
       LED short leg (-): row 17 col e
    3. Wire: Pi GPIO 18 (pin 12) ───→ row 16 col a (same row as resistor)
    4. Wire: Breadboard "-" rail ───→ row 17 col e (same row as LED short leg)
```

**Repeat for other LEDs in different rows:**

```
    YELLOW LED (Starting — GPIO 23)
    1. Resistor: row 20 col a → row 20 col d
    2. LED long leg: row 20 col e, short leg: row 21 col e
    3. Wire: Pi GPIO 23 (pin 16) → row 20 col a
    4. Wire: "-" rail → row 21 col e

    RED LED (Shutdown/Error — GPIO 24)
    1. Resistor: row 24 col a → row 24 col d
    2. LED long leg: row 24 col e, short leg: row 25 col e
    3. Wire: Pi GPIO 24 (pin 18) → row 24 col a
    4. Wire: "-" rail → row 25 col e
```

---

## Checklist Before Power On

- [ ] Pi is powered off
- [ ] GND wire: Pi pin 6 → breadboard "-" rail
- [ ] Button 1: GPIO 17 → button → GND rail (restart/shutdown)
- [ ] Button 2: GPIO 27 → button → GND rail (next instrument)
- [ ] Button 3: GPIO 22 → button → GND rail (prev instrument)
- [ ] Green LED: GPIO 18 → 220Ω resistor → LED → GND rail
- [ ] Yellow LED: GPIO 23 → 220Ω resistor → LED → GND rail
- [ ] Red LED: GPIO 24 → 220Ω resistor → LED → GND rail
- [ ] LED long legs (+) face toward the resistor side
- [ ] No bare wires touching each other

**Power on the Pi and run:**
```bash
cd /home/pi/piano-pi-brain && python3 piano_pi.py
```

You should see the **yellow LED blink** during startup, then **green LED solid** when ready!
