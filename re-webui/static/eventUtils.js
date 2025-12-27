var clicked_register;

// Equivalent to $(document).ready()
document.addEventListener('DOMContentLoaded', () => {
    const sidenav = document.querySelector('div.sidenav');
    const activeFunc = document.getElementById(func_to_download);

    if (activeFunc && sidenav) {
        // Highlight active function
        activeFunc.style.backgroundColor = "green";
        activeFunc.style.color = "yellow";

        // Scroll to active function (offset mimicking the -400 logic)
        const scrollPos = activeFunc.offsetTop - 400;
        sidenav.scrollTop = scrollPos;
    }

    // Initial load of xrefs
    if (typeof get_xrefs_from === 'function') get_xrefs_from(func_to_download);
    if (typeof get_xrefs_to === 'function') get_xrefs_to(func_to_download);

    const cfgContainer = document.querySelector("div.cfg");
    if (!cfgContainer) return;

    /**
     * FIX: Disable D3's default double-click zoom.
     */
    const disableD3DblClick = () => {
        const svgs = document.querySelectorAll("svg");
        svgs.forEach(svg => {
            if (typeof d3 !== 'undefined') {
                d3.select(svg).on("dblclick.zoom", null);
            }
        });
    };

    disableD3DblClick();
    const d3Observer = new MutationObserver(() => {
        disableD3DblClick();
    });
    d3Observer.observe(cfgContainer, { childList: true, subtree: true });

    // --- EVENT DELEGATION: CLICK ---
    cfgContainer.addEventListener('click', (event) => {
        const target = event.target;

        // 1. Register Variable Highlighting
        const regVar = target.closest('a.token.register.variable');
        if (regVar) {
            clicked_register = regVar.textContent.trim();

            // Highlight all matching registers across the document
            const allRegs = document.querySelectorAll('a.token.register.variable');
            allRegs.forEach(reg => {
                // Check inner content for the register name
                const children = Array.from(reg.childNodes);
                let foundMatch = false;

                children.forEach(child => {
                    if (child.textContent && child.textContent.includes(clicked_register)) {
                        child.parentElement.style.backgroundColor = "red";

                        // Handle de-obfuscation (removing blur)
                        const spanId = child.id;
                        if (spanId) {
                            const obfuscatedSpans = document.querySelectorAll(`span[id="${spanId}"].token.generic`);
                            obfuscatedSpans.forEach(s => s.style.filter = 'none');
                            if (typeof spanIds !== 'undefined') spanIds.push(spanId);
                        }
                        foundMatch = true;
                    }
                });

                if (!foundMatch) {
                    reg.style.backgroundColor = "";
                    // Clear nested background if necessary
                    Array.from(reg.children).forEach(c => c.style.backgroundColor = "");
                }
            });
            return;
        }

        // 2. Instruction Address Selection (EIP Marker)
        const addrToken = target.closest('span.token.address');
        if (addrToken) {
            addrToken.style.backgroundColor = "yellow";

            // Update global EIP reference
            const firstChild = addrToken.firstElementChild;
            if (firstChild) eip = firstChild.id;

            if (typeof exEipElement !== 'undefined' && exEipElement) {
                exEipElement.style.backgroundColor = "";
            }
            exEipElement = addrToken;
            return;
        }
    });

    // --- EVENT DELEGATION: MOUSE OVER (For Node Tracking) ---
    cfgContainer.addEventListener('mouseover', (event) => {
        const node = event.target.closest('g.node');
        if (node) {
            if (typeof selected === 'function') {
                selected(node);
            }
        }
    });
});