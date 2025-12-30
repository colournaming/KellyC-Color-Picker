# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KellyC Color Picker is a standalone HTML5 canvas-based color picker widget that uses the HSV color model. It's a single-file JavaScript library with no dependencies, designed to be scalable and work on mobile devices.

## Architecture

### Core Structure

The entire library is contained in a single constructor function `KellyColorPicker(cfg)` in `html5kellycolorpicker.js` (~2700 lines). The architecture uses:

- **Object-oriented closure pattern**: All state and methods are encapsulated within the constructor function
- **Canvas-based rendering**: Uses HTML5 Canvas API for all visual components
- **Event-driven model**: Custom event system for user interactions and color changes

### Key Components

The color picker is composed of several interactive geometric figures, each with their own object:

1. **Wheel** - The outer color wheel ring for hue selection
   - `wheel.draw()` - Renders the hue ring
   - `wheel.isDotIn(dot)` - Hit detection for mouse/touch events
   - Uses cached `wheel.imageData` to avoid re-rendering

2. **SV Figure** - Saturation/Value selector (center area)
   - Two implementations: `getSvFigureQuad()` (square) and `getSvFigureTriangle()` (triangle)
   - Each has: `draw()`, `dotToSv(dot)`, `svToDot(sv)`, `isDotIn(dot)`, `updateSize()`, `limitDotPosition(dot)`
   - Switched via `setMethod()` public method or style switch button

3. **Alpha Slider** - Optional transparency slider (right side when enabled)
   - `alphaSlider.draw()`, `alphaSlider.dotToAlpha()`, `alphaSlider.alphaToDot()`
   - Enabled via `alphaSlider: true` config option

4. **Color Savers** - Optional triangle buttons (bottom corners) to store colors
   - Created via `initColorSaver(align, selected, color)`
   - Each has its own `draw()`, `isDotIn()`, `updateSize()` methods

5. **Style Switch** - Optional button to toggle between quad/triangle SV methods
   - Created via `initStyleSwitch()`

6. **Cursors** - Visual indicators for current selection
   - `wheelCursor` - Shows selected hue position on wheel
   - `svCursor` - Shows selected saturation/value position
   - Custom cursor system via `svCursorMouse` with `initSvCursor()` and `initStandartCursor()`

### Color Management

Colors are maintained in three parallel representations:
- `hsv` - Hue, Saturation, Value object
- `rgb` - Red, Green, Blue object
- `hex` - Hex string (e.g., '#ff0000')
- `a` - Alpha value (0-1)

Converters between formats:
- `hsvToRgb(h, s, v)` / `rgbToHsv(r, g, b)`
- `hexToRgb(hex)` / `rgbToHex(color)`
- `readColorData(cString, falseOnFail)` - Parses various color string formats

### Rendering Strategy

The library uses a multi-layered caching approach to optimize performance:

1. **Helper Canvas** (`canvasHelper`) - Offscreen canvas for pre-rendering components
2. **Image Data Cache** - Components store their rendered `ImageData` to avoid redrawing
3. **Rendered Flag** - `rendered` boolean tracks if the base interface needs redrawing
4. **canvasHelperData** - Stores the complete rendered interface (without cursors/alpha slider)

When color changes, only cursors are redrawn. Full re-renders only happen on resize or method switch.

### Input Integration

The picker can attach to DOM input elements in two ways:

1. **Direct Canvas** - `place` config points to a canvas or container element
2. **Popup Mode** - Attaches to an input, shows picker in a popup div on click
   - Popup positioning handled by `popUpShow(e)` / `popUpClose(e)`
   - Managed via `popup.tag` object

Input synchronization:
- `updateInput()` - Updates input value when picker color changes
- `inputEdit()` - Updates picker when input value changes manually
- Format controlled by `inputFormat` ('mixed', 'hex', 'rgba')

### Event System

Two event systems coexist:

1. **Internal Events** (`events` array) - DOM event listeners managed by library
   - Added via `addEventListner(object, event, callback, prefix)`
   - Removed via `removeEventListener(object, event, prefix)`
   - Prefixed by action type (e.g., 'popup_', 'input_edit_', 'action_process_')

2. **User Events** (`userEvents` object) - Callbacks for library consumers
   - Added via `addUserEvent(event, callback)` public method
   - Triggered at key points: color change, method switch, etc.

### Mouse/Touch Handling

Interaction handled through several event handlers:
- `mouseDownEvent()` - Initiates drag, determines which component was clicked
- `mouseMoveRest()` / `wheelMouseMove()` / `svMouseMove()` / `alphaMouseMove()` - Handle dragging
- `mouseUpEvent()` / `wheelMouseUp()` / `svMouseUp()` / `alphaMouseUp()` - End drag
- `touchMoveEvent()` - Mobile touch support
- `drag` flag indicates active dragging state
- `cursorAnimReady` flag limits FPS via requestAnimationFrame

## Development

### Testing

To serve the color picker for testing:
```bash
uv run python -m http.server
```

Then open http://localhost:8000/examples/test_attach_to_input.html in your browser.

Available example pages:
- `examples/index.html` - List of all examples
- `examples/test_attach_to_input.html` - Basic usage with input binding
- `examples/test_popup.html` - Popup mode
- `examples/test_resize_onchange_event.html` - Alpha slider and resize
- `examples/test_colorsavers.html` - Color saver buttons
- `examples/test_create_and_destroy.html` - Dynamic creation/destruction
- `examples/test_destroy.html` - Destroy and resize testing
- `examples/test_one_colorpicer_and_multiple_inputs.html` - Multi-input binding

### File Structure

- `html5kellycolorpicker.js` - Full source (unminified)
- `html5kellycolorpicker.min.js` - Minified version
- `examples/` - Demo HTML files
- Examples include the minified version via `<script src="../html5kellycolorpicker.min.js"></script>`

### Building

To build the minified JavaScript file:
```bash
uv run python scripts/minify.py
```

### Configuration Options

The constructor accepts a config object with these key options:
- `place` - Canvas element ID or DOM element to render into
- `input` - Input element ID or DOM element to bind to
- `size` - Wheel block size in pixels (default: 200)
- `method` - 'quad' or 'triangle' for SV figure style
- `alpha` / `alphaSlider` - Enable transparency slider
- `inputColor` - Whether to update input color
- `inputFormat` - 'mixed', 'hex', or 'rgba'
- `userEvents` - Object of event callbacks
- `changeCursor` - Enable custom cursor
- `popupClass` - Custom CSS class for popup

### Public API

Key public methods on the KellyColorPicker instance:
- `setColor(color, manualEnter)` / `setColorByHex(hex, manualEnter)` - Set current color
- `setAlpha(alpha)` - Set transparency
- `getCurColorHex()` / `getCurColorRgb()` / `getCurColorHsv()` / `getCurColorRgba()` - Get current color
- `resize(size, refresh)` - Resize picker
- `setMethod(method)` - Switch between 'quad' and 'triangle'
- `updateView(dropBuffer)` - Force redraw
- `destroy()` - Clean up and remove picker
- `addUserEvent(event, callback)` / `removeUserEvent(event)` - Manage callbacks

### Static Properties

`KellyColorPicker.cursorLock` and `KellyColorPicker.activePopUp` - Global state for cursor and popup management
