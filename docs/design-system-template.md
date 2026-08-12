# POS System Design System & UI/UX Blueprint

**Artifact:** Design System & Theme Specification  
**Applies to:** Both POS Register (Touch/Keyboard Cashier Terminal) and Cloud Back-Office (Administrative Console)  
**Status:** Locked. Every token, geometry, component rule, and architectural directive in this document is explicit and implementation-ready.

---

## 1. System Vision & Ergonomic Goals

### 1.1 Dual POS Domain Context & Ergonomic Objectives

A Point of Sale (POS) ecosystem operates across two distinct physical and operational environments. This specification provides exact, non-ambiguous design rules for both:

| Metric / Dimension | POS Register (Cashier Terminal) | Cloud Back-Office (Admin Console) |
|---|---|---|
| **Input Modality** | Touchscreen (gloved/rapid tap) + Numpad / Barcode Scanner | Keyboard + Mouse / Trackpad |
| **User Mindset** | High speed, zero distraction, rapid customer turnaround | Deep analytical focus, data-dense manipulation |
| **Session Length** | Seconds per transaction (hundreds per shift) | Minutes to hours continuous management |
| **Lighting Context** | Variable (bright daylight, dim bar/countertop) | Standard office / desktop environments |
| **Ergonomic Priority** | High contrast, large touch targets (≥44px), instant feedback | Maximum information density, tight table scanning |
| **Primary Controls** | Numpad, Item Grid, Order Summary List, Quick Action CTAs | Data Tables, Filter Bars, Drawers, Multi-step Forms |

### 1.2 Core Architectural Principles

1. **Strict Monochrome Foundation; Semantic Color as Signal Only:**  
   The interface relies exclusively on a clean monochrome base palette (White, Black, Grayscale). Color is never used decoratively. When green, amber, red, or blue appears, it represents a precise semantic system signal (Success, Warning, Danger, Info).

2. **Black/White Primary Actions — Never Decorative Accents:**  
   The primary action CTA is solid black in light mode and solid white in dark mode (`bg-ink-primary text-ink-inverse`). This prevents primary buttons from competing visually with critical semantic status indicators.

3. **Border-Driven Hierarchy over Layered Shadows:**  
   Surfaces and containers are separated by high-contrast 1px borders (`border-subtle` and `border-default`). Drop shadows are strictly reserved for floating overlay elements (dropdowns, popovers, modals, toasts).

4. **Tabular Financial & Numerical Rigor:**  
   All numerical data (prices, totals, quantities, SKU numbers, timestamps) must use tabular figure settings (`font-variant-numeric: tabular-nums`). Financial figures must always be right-aligned and formatted to exactly two decimal places.

5. **Universal Keyboard Accessibility & Focus Visibility:**  
   Every interactive component enforces a visible focus outline (`2px solid var(--color-ink-primary)` with `2px offset`). Keyboard navigation (`Tab`, `Enter`, `Space`, `Esc`, Arrow keys) is a first-class requirement across all views.

6. **DRY Architecture, Clean File Directories & Standardized Route Auth:**  
   Component logic, design tokens, and authentication handling follow strict DRY (Don't Repeat Yourself) principles. File directory structures are modularly partitioned, and authentication protection is enforced standardly directly at the route definition layer.

---

## 2. Design Tokens

### Color Palette (CSS Variables / Tailwind Config Format)

The system utilizes Tailwind CSS v4's CSS-first `@theme inline` declaration mechanism. All colors are derived from a true neutral grayscale palette with no blue or warm tint.

#### Grayscale Base Values

```
50  #fafafa    200 #e5e5e5    400 #a3a3a3    600 #525252    800 #262626    950 #0a0a0a
100 #f5f5f5    300 #d4d4d4    500 #737373    700 #404040    900 #171717
```

#### Light & Dark Mode Surface, Border & Ink Tokens

| Token | Light Value | Dark Value | Purpose & Target Application |
|---|---|---|---|
| `--canvas` | `#fafafa` | `#0a0a0a` | Global application canvas background |
| `--surface` | `#ffffff` | `#171717` | Card backgrounds, table bodies, drawer containers, inputs |
| `--surface-sunken` | `#f5f5f5` | `#0a0a0a` | Table headers, inset keypads, code blocks, well backgrounds |
| `--surface-raised` | `#ffffff` | `#262626` | Floating elements: modals, popovers, dropdowns, toasts |
| `--surface-hover` | `#f5f5f5` | `#262626` | Interactive hover state for rows, ghost buttons, menu items |
| `--border-subtle` | `#e5e5e5` | `#262626` | Table row dividers, subtle card separators |
| `--border-default` | `#d4d4d4` | `#404040` | Outer card boundaries, fieldset containers |
| `--border-control` | `#8a8a8a` | `#737373` | **Form input, checkbox, select boundaries (Contrast ≥ 3:1)** |
| `--ink-primary` | `#0a0a0a` | `#fafafa` | Primary headings, body copy, active text, primary CTA fill |
| `--ink-secondary` | `#525252` | `#d4d4d4` | Secondary copy, form labels, table headers, breadcrumbs |
| `--ink-tertiary` | `#737373` | `#a3a3a3` | Input placeholders, helper text, monetary symbols |
| `--ink-inverse` | `#ffffff` | `#0a0a0a` | Text rendered on top of solid primary backgrounds |

#### Semantic Status Overlays

Semantic colors are restricted to feedback alerts, badges, status cells, and destructive actions.

| Semantic Token | Theme | Foreground (`fg`) | Background (`bg`) | Border (`border`) | Meaning |
|---|---|---|---|---|---|
| **Success** | Light | `#15803d` | `#f0fdf4` | `#86efac` | Order paid, payment verified, shift balanced, saved |
| | Dark | `#4ade80` | `#052e16` | `#166534` | |
| **Warning** | Light | `#b45309` | `#fffbeb` | `#fcd34d` | Low stock warning, cash variance detected, pending hold |
| | Dark | `#fbbf24` | `#451a03` | `#92400e` | |
| **Danger** | Light | `#b91c1c` | `#fef2f2` | `#fca5a5` | Order voided, refund processed, delete confirm, error |
| | Dark | `#f87171` | `#450a0a` | `#991b1b` | |
| **Info** | Light | `#1d4ed8` | `#eff6ff` | `#93c5fd` | Payment pending, system notice, info alert |
| | Dark | `#60a5fa` | `#172554` | `#1e40af` | |

#### Complete Tailwind v4 `src/index.css` Implementation

```css
@import 'tailwindcss';
@import '@fontsource-variable/inter';
@import '@fontsource-variable/jetbrains-mono';

@custom-variant dark (&:where(.dark, .dark *));

:root {
  --canvas:         #fafafa;
  --surface:        #ffffff;
  --surface-sunken: #f5f5f5;
  --surface-raised: #ffffff;
  --surface-hover:  #f5f5f5;

  --border-subtle:  #e5e5e5;
  --border-default: #d4d4d4;
  --border-control: #8a8a8a;

  --ink-primary:    #0a0a0a;
  --ink-secondary:  #525252;
  --ink-tertiary:   #737373;
  --ink-inverse:    #ffffff;

  --success-fg: #15803d;  --success-bg: #f0fdf4;  --success-border: #86efac;
  --warning-fg: #b45309;  --warning-bg: #fffbeb;  --warning-border: #fcd34d;
  --danger-fg:  #b91c1c;  --danger-bg:  #fef2f2;  --danger-border:  #fca5a5;
  --info-fg:    #1d4ed8;  --info-bg:    #eff6ff;  --info-border:    #93c5fd;

  color-scheme: light;
}

.dark {
  --canvas:         #0a0a0a;
  --surface:        #171717;
  --surface-sunken: #0a0a0a;
  --surface-raised: #262626;
  --surface-hover:  #262626;

  --border-subtle:  #262626;
  --border-default: #404040;
  --border-control: #737373;

  --ink-primary:    #fafafa;
  --ink-secondary:  #d4d4d4;
  --ink-tertiary:   #a3a3a3;
  --ink-inverse:    #0a0a0a;

  --success-fg: #4ade80;  --success-bg: #052e16;  --success-border: #166534;
  --warning-fg: #fbbf24;  --warning-bg: #451a03;  --warning-border: #92400e;
  --danger-fg:  #f87171;  --danger-bg:  #450a0a;  --danger-border:  #991b1b;
  --info-fg:    #60a5fa;  --info-bg:    #172554;  --info-border:    #1e40af;

  color-scheme: dark;
}

@theme inline {
  --color-canvas:         var(--canvas);
  --color-surface:        var(--surface);
  --color-surface-sunken: var(--surface-sunken);
  --color-surface-raised: var(--surface-raised);
  --color-surface-hover:  var(--surface-hover);

  --color-border-subtle:  var(--border-subtle);
  --color-border-default: var(--border-default);
  --color-border-control: var(--border-control);

  --color-ink-primary:    var(--ink-primary);
  --color-ink-secondary:  var(--ink-secondary);
  --color-ink-tertiary:   var(--ink-tertiary);
  --color-ink-inverse:    var(--ink-inverse);

  --color-success-fg:     var(--success-fg);
  --color-success-bg:     var(--success-bg);
  --color-success-border: var(--success-border);
  --color-warning-fg:     var(--warning-fg);
  --color-warning-bg:     var(--warning-bg);
  --color-warning-border: var(--warning-border);
  --color-danger-fg:      var(--danger-fg);
  --color-danger-bg:      var(--danger-bg);
  --color-danger-border:  var(--danger-border);
  --color-info-fg:        var(--info-fg);
  --color-info-bg:        var(--info-bg);
  --color-info-border:    var(--info-border);

  --font-sans: 'Inter Variable', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono Variable', monospace;

  --text-micro:    0.6875rem;  --text-micro--line-height:    0.875rem;
  --text-caption:  0.75rem;    --text-caption--line-height:  1rem;
  --text-body-sm:  0.8125rem;  --text-body-sm--line-height:  1.125rem;
  --text-body:     0.875rem;   --text-body--line-height:     1.25rem;
  --text-lead:     1rem;       --text-lead--line-height:     1.5rem;
  --text-h3:       1.125rem;   --text-h3--line-height:       1.625rem;
  --text-h2:       1.25rem;    --text-h2--line-height:       1.75rem;
  --text-h1:       1.5rem;     --text-h1--line-height:       2rem;
  --text-display:  1.875rem;   --text-display--line-height:  2.25rem;

  --radius-xs:  0.125rem;
  --radius-sm:  0.25rem;
  --radius-md:  0.375rem;
  --radius-lg:  0.5rem;
  --radius-xl:  0.75rem;
  --radius-2xl: 1rem;

  --shadow-e1: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-e2: 0 4px 8px -2px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06);
  --shadow-e3: 0 16px 32px -8px rgb(0 0 0 / 0.12), 0 4px 8px -4px rgb(0 0 0 / 0.08);

  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter:    cubic-bezier(0, 0, 0.2, 1);
  --ease-exit:     cubic-bezier(0.4, 0, 1, 1);
}

@layer base {
  * { border-color: var(--color-border-subtle); }
  html { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
  body {
    margin: 0;
    background-color: var(--color-canvas);
    color: var(--color-ink-primary);
    font-family: var(--font-sans);
    font-size: var(--text-body);
    line-height: var(--text-body--line-height);
  }
  .tabular, input[type='number'] {
    font-variant-numeric: tabular-nums;
    font-feature-settings: 'tnum' 1;
  }
  :focus-visible {
    outline: 2px solid var(--color-ink-primary);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
  }
}
```

---

### Typography Scale

Two self-hosted npm packages handle typography (`@fontsource-variable/inter` and `@fontsource-variable/jetbrains-mono`).

- **Inter Variable:** All standard user interface labels, table content, form fields, headings.
- **JetBrains Mono Variable:** Technical identifiers, SKUs, order numbers, schema names, JSON audit logs, and numerical figures requiring strict tabular grid alignment.

| Type Token | Font Size | Line Height | Font Weight | Recommended Usage |
|---|---|---|---|---|
| `text-display` | 30px (`1.875rem`) | 36px (`2.25rem`) | `600` / `700` | High-impact Stat Tile numbers, Numpad display values |
| `text-h1` | 24px (`1.5rem`) | 32px (`2.0rem`) | `600` | Primary page headers, POS cart grand total headline |
| `text-h2` | 20px (`1.25rem`) | 28px (`1.75rem`) | `600` | Section titles, modal dialog titles |
| `text-h3` | 18px (`1.125rem`) | 26px (`1.625rem`) | `600` | Drawer titles, card headers |
| `text-lead` | 16px (`1.0rem`) | 24px (`1.5rem`) | `400` / `500` | Empty-state descriptive text, high-visibility CTA labels |
| **`text-body`** | **14px (`0.875rem`)** | **20px (`1.25rem`)** | **`400` / `500`** | **System Default.** Table cells, standard inputs, buttons |
| `text-body-sm` | 13px (`0.8125rem`) | 18px (`1.125rem`) | `400` | Compact table rows, secondary item modifiers, metadata |
| `text-caption` | 12px (`0.75rem`) | 16px (`1.0rem`) | `500` | Form field labels, table header columns, status badges |
| `text-micro` | 11px (`0.6875rem`) | 14px (`0.875rem`) | `600` | Uppercase section eyebrows, stat tile metadata |

#### Tabular Figure Formatting Rules

1. Every price or monetary value must format using `tabular-nums` right-aligned, displaying exactly two decimal digits (`$1,240.50`, `$0.00`).
2. Currency symbols (`$`) are set in `text-ink-tertiary` to isolate the numeric alignment column.
3. Quantity values display `tabular-nums` right-aligned, supporting up to 3 decimals for fractional stock (`1.250 kg`).

---

### Spacing, Radius & Elevation

#### Spacing Scale (4px Base Grid)

Tailwind v4 derives default spacing utilities based on 4px (`0.25rem`) increments:

| Token | px Value | Application Context |
|---|---|---|
| `1` | 4px | Micro gap: badge icon to text label, tag padding |
| `1.5` | 6px | Tight gap: inline field hint offset, form field label gap |
| `2` | 8px | Standard inline gap: button icon to label, input internal padding |
| `3` | 12px | Cell padding (compact table), input side padding |
| `4` | 16px | Card padding (compact), gap between form controls |
| `5` | 20px | Table cell padding (comfortable row height) |
| `6` | 24px | Card padding (default), section padding |
| `8` | 32px | Major section gap, page gutter |
| `10` | 40px | High-density page container top spacing |
| `12` | 48px | Keypad button heights, major layout blocks |

#### Control Height & Density Constants

- **Touch / Register Control (`lg`):** `44px` (`h-11`) — Mandatory for POS touchscreen & numpad targets.
- **Default Desktop Control (`md`):** `36px` (`h-9`) — Form inputs, buttons, toolbar selectors.
- **Compact Table Control (`sm`):** `32px` (`h-8`) — Table row actions, filter pill buttons.
- **Comfortable Table Row:** `44px` height.
- **Compact Table Row:** `36px` height.

#### Border Radius Hierarchy

- `rounded-xs`: `2px` (Checkboxes)
- `rounded-sm`: `4px` (Focus outlines, badge indicators)
- `rounded-md`: `6px` (**Buttons, inputs, selects, dropdown items**)
- `rounded-lg`: `8px` (Cards, table containers, stat tiles)
- `rounded-xl`: `12px` (Modals, slide-over drawers)
- `rounded-2xl`: `16px` (Auth dialog cards)
- `rounded-full`: `9999px` (Avatars, pills, switches, numpad buttons)

#### Elevation Hierarchy

- `e0` (Flat): No shadow, 1px `border-subtle` or `border-default` boundary. Used for cards and table bodies.
- `shadow-e1`: `0 1px 2px 0 rgb(0 0 0 / 0.05)`. Sticky headers and subtle hover elevation.
- `shadow-e2`: `0 4px 8px -2px rgb(0 0 0 / 0.08)`. Dropdowns, popovers, tooltips.
- `shadow-e3`: `0 16px 32px -8px rgb(0 0 0 / 0.12)`. Floating modals, side drawers, toast notifications.

---

## 3. Iconography Guidelines

The system utilizes `lucide-react` (v1.31.0) exclusively.

### 3.1 Size and Stroke Rules

- **14px Icon:** `strokeWidth={2}` — Small badge indicators, inline input clear buttons.
- **16px Icon:** `strokeWidth={1.5}` — **Default.** Button icons, table row actions, dropdown menu items.
- **20px Icon:** `strokeWidth={1.5}` — Navigation items, section header icons.
- **24px Icon:** `strokeWidth={1.5}` — Stat tile primary icons, empty state graphic illustrations.

### 3.2 Icon Mapping Table

| Action / Context | Lucide Icon Name | Notes |
|---|---|---|
| Dashboard Overview | `LayoutDashboard` | Navigation bar |
| Branches | `Store` | Navigation & headers |
| Employees / Users | `Users` | Navigation & headers |
| Employee Role / Permission | `ShieldCheck` | Permission gating |
| Products Catalogue | `Package` | Product management |
| Recipes / Ingredients | `ChefHat` | Recipe builder |
| Warehouse Stock | `Warehouse` / `Boxes` | Stock management |
| Sales Reports | `TrendingUp` | Analytics |
| Shift Reports | `Clock` | Shift audit |
| System Settings | `Settings` | Workspace config |
| Create / Add Item | `Plus` | Primary CTA |
| Edit Record | `SquarePen` | Row action |
| Delete Record | `Trash2` | Destructive CTA |
| Confirm / Save | `Check` | Submit feedback |
| Cancel / Close | `X` | Dismiss button |
| Search Input | `Search` | Filter bar |
| Filter Actions | `ListFilter` | Filter dropdown |
| Unsorted / Sort Active | `ChevronsUpDown` / `ArrowUp` / `ArrowDown` | Table headers |
| Row Menu Overflow | `Ellipsis` | Row menu |
| Success State | `CircleCheck` | **Never use legacy `CheckCircle`** |
| Warning State | `TriangleAlert` | Low stock alert |
| Danger / Error State | `CircleAlert` | Validation failure |
| Loading Spinner | `LoaderCircle` | Pair with `animate-spin` |
| Numpad Backspace | `Delete` | POS Numpad |
| Numpad Clear | `RotateCcw` | POS Numpad reset |
| Hold Order | `PauseCircle` | Register order action |
| Pay Cash | `Banknote` | Checkout payment |
| Pay Card | `CreditCard` | Checkout payment |

---

## 4. Component Design Specifications

### 4.1 Base Primitives

#### Button

```tsx
// src/components/ui/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { LoaderCircle } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

const button = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium whitespace-nowrap ' +
    'transition-[background-color,border-color,transform] duration-[120ms] ease-standard ' +
    'active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variant: {
        primary:   'bg-ink-primary text-ink-inverse hover:opacity-90',
        secondary: 'bg-surface text-ink-primary border border-border-control hover:bg-surface-hover',
        ghost:     'bg-transparent text-ink-secondary hover:bg-surface-hover hover:text-ink-primary',
        danger:    'bg-danger-fg text-white hover:opacity-90',
        link:      'bg-transparent text-ink-primary underline underline-offset-4 hover:opacity-70',
      },
      size: {
        sm:   'h-8 px-3 text-body-sm',
        md:   'h-9 px-4 text-body',
        lg:   'h-11 px-6 text-lead',
        icon: 'h-9 w-9 p-0 aspect-square',
      },
    },
    defaultVariants: { variant: 'secondary', size: 'md' },
  }
);

type Props = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof button> & { loading?: boolean; icon?: ReactNode };

export function Button({ className, variant, size, loading, icon, children, disabled, ...rest }: Props) {
  return (
    <button
      className={cn(button({ variant, size }), className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading ? <LoaderCircle size={16} strokeWidth={1.5} className="animate-spin" aria-hidden /> : icon}
      {children}
    </button>
  );
}
```

#### StatusBadge

```tsx
// src/components/ui/StatusBadge.tsx
import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

type Variant = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

const styles: Record<Variant, string> = {
  neutral: 'bg-surface-sunken text-ink-secondary border-border-subtle',
  success: 'bg-success-bg text-success-fg border-success-border',
  warning: 'bg-warning-bg text-warning-fg border-warning-border',
  danger:  'bg-danger-bg text-danger-fg border-danger-border',
  info:    'bg-info-bg text-info-fg border-info-border',
};

export function StatusBadge({ variant = 'neutral', icon, children }: { variant?: Variant; icon?: ReactNode; children: ReactNode }) {
  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-caption font-medium border', styles[variant])}>
      {icon}
      <span>{children}</span>
    </span>
  );
}
```

---

### 4.2 POS Register Ergonomic Components

#### Keypad / Numpad Component

Designed for touch cashiers and quick price/cash tender entry:

```tsx
// src/components/ui/Keypad.tsx
import { Button } from './Button';
import { Delete, RotateCcw } from 'lucide-react';

interface KeypadProps {
  onKeyPress: (key: string) => void;
  onClear: () => void;
  onBackspace: () => void;
  onSubmit?: () => void;
  submitLabel?: string;
}

export function Keypad({ onKeyPress, onClear, onBackspace, onSubmit, submitLabel = 'Enter' }: KeypadProps) {
  const keys = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '00', '.'];

  return (
    <div className="flex flex-col gap-2 p-3 bg-surface-sunken rounded-xl border border-border-default w-full max-w-[320px]">
      <div className="grid grid-cols-3 gap-2">
        {keys.map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => onKeyPress(k)}
            className="h-12 bg-surface hover:bg-surface-hover active:scale-95 text-h2 font-semibold text-ink-primary rounded-lg border border-border-default shadow-e1 transition-all flex items-center justify-center cursor-pointer select-none"
          >
            {k}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2 pt-1">
        <Button variant="secondary" size="lg" className="h-12" onClick={onClear}>
          <RotateCcw size={18} /> Clear
        </Button>
        <Button variant="secondary" size="lg" className="h-12" onClick={onBackspace}>
          <Delete size={18} /> Back
        </Button>
        <Button variant="primary" size="lg" className="h-12 font-bold" onClick={onSubmit}>
          {submitLabel}
        </Button>
      </div>
    </div>
  );
}
```

#### OrderSummaryList Component

High-density cashier cart breakdown displaying selected items, options, unit price, quantity adjustments, line discounts, and grand totals with exact tabular figures.

```tsx
// src/components/pos/OrderSummaryList.tsx
import { Plus, Minus, Trash2 } from 'lucide-react';

export interface CartItem {
  id: string;
  name: string;
  unitPrice: number;
  quantity: number;
  modifiers?: string[];
}

interface OrderSummaryListProps {
  items: CartItem[];
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  onUpdateQty: (id: string, delta: number) => void;
  onRemoveItem: (id: string) => void;
}

export function OrderSummaryList({ items, subtotal, tax, discount, total, onUpdateQty, onRemoveItem }: OrderSummaryListProps) {
  return (
    <div className="flex flex-col h-full bg-surface border border-border-default rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-surface-sunken border-b border-border-subtle flex items-center justify-between">
        <h2 className="text-h3 font-semibold text-ink-primary">Current Order</h2>
        <span className="text-caption text-ink-secondary">{items.length} items</span>
      </div>

      <div className="flex-1 overflow-y-auto divide-y divide-border-subtle p-2">
        {items.length === 0 ? (
          <div className="h-full flex items-center justify-center text-ink-tertiary text-body">Order cart is empty</div>
        ) : (
          items.map((item) => (
            <div key={item.id} className="py-2.5 px-2 flex items-center justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-body font-medium text-ink-primary truncate">{item.name}</div>
                {item.modifiers && item.modifiers.length > 0 && (
                  <div className="text-caption text-ink-tertiary">{item.modifiers.join(', ')}</div>
                )}
                <div className="text-caption text-ink-secondary tabular-nums">${item.unitPrice.toFixed(2)} ea</div>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => onUpdateQty(item.id, -1)}
                  className="w-7 h-7 rounded-md bg-surface-sunken border border-border-control flex items-center justify-center hover:bg-surface-hover active:scale-95 text-ink-primary"
                >
                  <Minus size={14} />
                </button>
                <span className="w-8 text-center text-body font-semibold tabular-nums">{item.quantity}</span>
                <button
                  onClick={() => onUpdateQty(item.id, 1)}
                  className="w-7 h-7 rounded-md bg-surface-sunken border border-border-control flex items-center justify-center hover:bg-surface-hover active:scale-95 text-ink-primary"
                >
                  <Plus size={14} />
                </button>
              </div>

              <div className="text-right min-w-[70px]">
                <div className="text-body font-semibold text-ink-primary tabular-nums">
                  ${(item.unitPrice * item.quantity).toFixed(2)}
                </div>
              </div>

              <button onClick={() => onRemoveItem(item.id)} className="text-ink-tertiary hover:text-danger-fg p-1">
                <Trash2 size={16} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="p-4 bg-surface-sunken border-t border-border-subtle space-y-2">
        <div className="flex justify-between text-body-sm text-ink-secondary">
          <span>Subtotal</span>
          <span className="tabular-nums font-mono">${subtotal.toFixed(2)}</span>
        </div>
        {discount > 0 && (
          <div className="flex justify-between text-body-sm text-danger-fg">
            <span>Discount</span>
            <span className="tabular-nums font-mono">-${discount.toFixed(2)}</span>
          </div>
        )}
        <div className="flex justify-between text-body-sm text-ink-secondary">
          <span>Tax (10%)</span>
          <span className="tabular-nums font-mono">${tax.toFixed(2)}</span>
        </div>
        <div className="pt-2 border-t border-border-default flex justify-between items-center">
          <span className="text-h2 font-bold text-ink-primary">Total</span>
          <span className="text-h1 font-bold text-ink-primary tabular-nums font-mono">${total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
```

---

### 4.3 Data Table & Cloud Back-Office Primitives

```tsx
// src/components/ui/DataTable.tsx
import { ReactNode } from 'react';
import { ChevronsUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Skeleton } from './Skeleton';

export interface Column<T> {
  key: string;
  header: string;
  align?: 'left' | 'right' | 'center';
  sortable?: boolean;
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  onSort?: (key: string) => void;
  emptyText?: string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  loading,
  sortColumn,
  sortDirection,
  onSort,
  emptyText = 'No data records found',
}: DataTableProps<T>) {
  return (
    <div className="w-full rounded-lg border border-border-default overflow-hidden bg-surface">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="bg-surface-sunken border-b border-border-subtle h-9">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-5 text-caption font-medium text-ink-secondary ${
                    col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                  }`}
                >
                  {col.sortable ? (
                    <button
                      onClick={() => onSort?.(col.key)}
                      className="inline-flex items-center gap-1.5 hover:text-ink-primary cursor-pointer select-none"
                    >
                      {col.header}
                      {sortColumn === col.key ? (
                        sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                      ) : (
                        <ChevronsUpDown size={14} className="text-ink-tertiary" />
                      )}
                    </button>
                  ) : (
                    col.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle text-body text-ink-primary">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="h-11">
                  {columns.map((col) => (
                    <td key={col.key} className="px-5 py-2">
                      <Skeleton className="h-4 w-full" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-5 py-12 text-center text-ink-tertiary">
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx} className="h-11 hover:bg-surface-hover transition-colors">
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-5 py-2 ${
                        col.align === 'right' ? 'text-right tabular-nums' : col.align === 'center' ? 'text-center' : 'text-left'
                      }`}
                    >
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## 5. Micro-Interactions & UX Motion

### 5.1 Standard Motion Tokens

- **Fast Transition (120ms):** `duration-[120ms] ease-standard`. Used for button active scale down (`scale-[0.98]`), surface background color changes, row hover states, and badge color transitions.
- **Medium Transition (180ms):** `duration-[180ms] ease-enter` / `ease-exit`. Used for modal overlays, dropdown popovers, tooltips, and toast enter/exit animations.
- **Slow Transition (240ms):** `duration-[240ms] ease-standard`. Used for slide-over drawers, full page section collapse, and sidebar menu toggles.

### 5.2 Motion Rules & Reduced Motion Fallback

- **Compositor Property Restriction:** Only transition `transform` and `opacity`. Never animate `width`, `height`, `margin`, or `padding` directly to prevent layout thrashing on high-density tables.
- **Reduced Motion Guard:** Under `prefers-reduced-motion: reduce`, all durations drop to `0.01ms`, disabling motion loops for accessibility compliance.

---

## 6. Execution Checklist for Developers

### 6.1 Repository Setup & CSS Token Configuration
- [ ] Install exact dependencies:
  ```bash
  npm install tailwindcss@4.3.3 @tailwindcss/vite@4.3.3 lucide-react@1.31.0 class-variance-authority@0.7.1 clsx@2.1.1 tailwind-merge@3.6.0 @fontsource-variable/inter@5.3.0 @fontsource-variable/jetbrains-mono@5.3.0
  ```
- [ ] Configure `vite.config.ts` with `@tailwindcss/vite` plugin and `@/` path alias.
- [ ] Configure `tsconfig.app.json` with matching `"paths": { "@/*": ["./src/*"] }`.
- [ ] Replace `src/index.css` with the exact token file from Section 2.1.
- [ ] Delete all legacy `*.module.css` files, `App.css`, and static demo assets (`hero.png`, `react.svg`).

### 6.2 Standardized Directory Architecture & DRY Rules
Maintain a strict, modular file directory structure:
```
src/
├── components/
│   ├── ui/               # Base reusable primitives (Button, Input, StatusBadge, DataTable, Keypad)
│   ├── layout/           # AppShell, Topbar, SidebarNav, PageHeader
│   └── pos/              # POS terminal components (OrderSummaryList, RegisterGrid)
├── context/              # Global state contexts (AuthContext, ThemeContext)
├── features/             # Feature domain modules
│   ├── auth/             # Login, Register, PaymentSuccess pages
│   ├── inventory/        # Stock management & items
│   ├── orders/           # Order processing & sales history
│   └── reports/          # Analytics & shift reports
├── hooks/                # Custom React hooks (useTheme, useAuth)
├── services/             # Axios API client & endpoints
└── types/                # TypeScript interface definitions
```

### 6.3 Standardizing Authentication Flows Directly in Routes

To eliminate ad-hoc, duplicated auth logic inside individual components, standardize route guards directly within the React Router tree:

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import LoginPage from '@/features/auth/pages/LoginPage';
import RegisterPage from '@/features/auth/pages/RegisterPage';
import PaymentSuccessPage from '@/features/auth/pages/PaymentSuccessPage';
import DashboardPage from '@/pages/DashboardPage';
import { Spinner } from '@/components/ui/Spinner';

// Route Guard: Protected Authorized Routes
function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-canvas">
        <Spinner size={24} />
      </div>
    );
  }
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

// Route Guard: Public-Only Auth Routes (Redirects logged-in users away from /login)
function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-canvas">
        <Spinner size={24} />
      </div>
    );
  }
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public-Only Auth Routes */}
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/payment-success" element={<PaymentSuccessPage />} />
          </Route>

          {/* Protected Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Route>

          {/* Fallback Catch-all Route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

- [ ] Wrap all protected application pages under `<Route element={<ProtectedRoute />}>`.
- [ ] Wrap all login/registration flows under `<Route element={<PublicOnlyRoute />}>`.
- [ ] Ensure `AuthProvider` is mounted at the top-level root so auth state flows standardly to all route hooks.
- [ ] Perform `npm run build` and `npm run lint` verification to confirm clean, error-free execution.
