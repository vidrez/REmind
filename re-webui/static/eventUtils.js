var clicked_register;


function obfuscate(id) {
    if (typeof spanIds === 'undefined') return;

    // 1. Blur all generic spans that were previously unblurred
    spanIds.forEach(spanId => {
        const spans = document.querySelectorAll(`span[id="${spanId}"].token.generic`);
        spans.forEach(s => s.style.filter = 'blur(8px)');
    });

    localStorage.setItem("addr", id);

    // 2. Unblur generic tokens within the current basic block (ID)
    const currentBlockTokens = document.querySelectorAll(`code[id="${id}"] span.token.generic`);
    currentBlockTokens.forEach(token => {
        token.style.filter = 'none';
    });

    // 3. Reset background color for all generic tokens
    const allGenericTokens = document.querySelectorAll('.token.generic');
    allGenericTokens.forEach(token => {
        token.style.background = "";
    });

    // Reset the tracker for unblurred spans
    spanIds = [];

    // 4. Ensure previous block is blurred if moving
    if (typeof previousBBid !== 'undefined' && previousBBid != 0 && previousBBid !== id) {
        const prevBlockTokens = document.querySelectorAll(`code[id="${previousBBid}"] span.token.generic`);
        prevBlockTokens.forEach(token => {
            token.style.filter = 'blur(8px)';
        });
    }

    previousBBid = id;
}

/**
 * Restore variable renames after Dagre-D3 re-renders.
 */
function restore_graph_rename_after_rendering(BBId) {
    if (typeof renameVariablesData === 'undefined' || !renameVariablesData) return;
    const dataArray = Array.isArray(renameVariablesData) ? renameVariablesData : Object.values(renameVariablesData);

    dataArray.forEach(item => {
        if (item.event === 'rename') {
            const addr = item.element;
            const value = item.value;
            const localContainers = document.querySelectorAll('span.token.local');
            localContainers.forEach(container => {
                const genericSpan = container.querySelector(`span[id="${addr}"].token.generic`);
                if (genericSpan) {
                    genericSpan.innerText = value;
                    const parentBlock = container.closest('code');
                    if (parentBlock) {
                        genericSpan.style.filter = (parentBlock.id === BBId) ? 'none' : 'blur(8px)';
                    }
                }
            });
        }
    });
}

/**
 * Fetch-based Note Management
 */
function storeit() {
    const noteArea = document.getElementById("notes_area");
    if (!noteArea) return;
    const note = noteArea.value;

    fetch(`${base_url}/storeNotes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ 'token': id, 'notes': note })
    })
        .then(r => { if (r.ok) alert("Notes saved!"); })
        .catch(e => console.error('Store error:', e));
}

async function downloadNotes() {
    try {
        const response = await fetch(`${base_url}/downloadNotes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ 'token': id })
        });
        if (!response.ok) return;
        const data = await response.text();
        const noteArea = document.getElementById("notes_area");
        if (noteArea) noteArea.value = data;
    } catch (e) { console.error('Download error:', e); }
}

// UI Initialization
document.addEventListener('DOMContentLoaded', () => {
    const sidenav = document.querySelector('div.sidenav');
    const activeFunc = document.getElementById(func_to_download);
    if (activeFunc && sidenav) {
        activeFunc.style.backgroundColor = "green";
        activeFunc.style.color = "yellow";
        sidenav.scrollTop = activeFunc.offsetTop - 400;
    }

    if (typeof get_xrefs_from === 'function') get_xrefs_from(func_to_download);
    if (typeof get_xrefs_to === 'function') get_xrefs_to(func_to_download);

    const cfgContainer = document.querySelector("div.cfg");
    if (!cfgContainer) return;

    // D3 Zoom Override
    const disableD3DblClick = () => {
        document.querySelectorAll("svg").forEach(svg => {
            if (typeof d3 !== 'undefined') d3.select(svg).on("dblclick.zoom", null);
        });
    };

    disableD3DblClick();
    const d3Observer = new MutationObserver(() => {
        disableD3DblClick();
    });
    d3Observer.observe(cfgContainer, { childList: true, subtree: true });

    // CLICK DELEGATION (Registers & EIP)
    cfgContainer.addEventListener('click', (event) => {
        const target = event.target;
        const regVar = target.closest('a.token.register.variable');
        if (regVar) {
            clicked_register = regVar.textContent.trim();
            document.querySelectorAll('a.token.register.variable').forEach(reg => {
                let found = false;
                Array.from(reg.childNodes).forEach(child => {
                    if (child.textContent && child.textContent.includes(clicked_register)) {
                        child.parentElement.style.backgroundColor = "red";
                        if (child.id) {
                            document.querySelectorAll(`span[id="${child.id}"].token.generic`).forEach(s => s.style.filter = 'none');
                            if (typeof spanIds !== 'undefined') spanIds.push(child.id);
                        }
                        found = true;
                    }
                });
                if (!found) {
                    reg.style.backgroundColor = "";
                    Array.from(reg.children).forEach(c => c.style.backgroundColor = "");
                }
            });
            return;
        }

        const addrToken = target.closest('span.token.address');
        if (addrToken) {
            addrToken.style.backgroundColor = "yellow";
            if (addrToken.firstElementChild) eip = addrToken.firstElementChild.id;
            if (typeof exEipElement !== 'undefined' && exEipElement) exEipElement.style.backgroundColor = "";
            exEipElement = addrToken;
        }
    });

    // MOUSEOVER (Node Focus)
    cfgContainer.addEventListener('mouseover', (event) => {
        const node = event.target.closest('g.node');
        if (node && typeof selected === 'function') selected(node);
    });
});

// KEYBOARD SHORTCUTS
document.addEventListener('keydown', (evt) => {
    if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') return;

    if (evt.key === "Escape" || evt.key === "Esc") {
        if (typeof myHistory !== 'undefined' && myHistory) {
            scrollToAddress(myHistory, scrollEventsEnum.ESC);
            if (typeof destination !== 'undefined') obfuscate(destination);
            myHistory = null;
        } else if (localStorage.getItem("myFunctionHistory") != 0) {
            relocate = 1;
            setTimeout(() => { if (typeof change_page === 'function') change_page(); }, 50);
        }
        return;
    }

    if (evt.key === 'c' && typeof eip !== 'undefined') {
        const codeId = typeof getBBbyAddress === 'function' ? getBBbyAddress(eip) : null;
        if (codeId && typeof exEipElement !== 'undefined' && exEipElement) {
            if (typeof cfg_comment === 'function') {
                cfg_comment(codeId, exEipElement);
                setTimeout(() => { if (typeof obfuscate === 'function') obfuscate(codeId); }, 150);
            }
        }
    }

    if (evt.key === 'r' && typeof exEipElement !== 'undefined' && exEipElement) {
        const firstChild = exEipElement.children[0];
        if (!firstChild) return;

        const cid = firstChild.id;
        let elemToRename = null;

        const genericSpans = document.querySelectorAll(`span[id="${cid}"].token.generic`);
        genericSpans.forEach(span => {
            if (span.parentElement && span.parentElement.classList.contains("local")) {
                elemToRename = span;
            }
        });

        if (elemToRename) {
            if (typeof rename === 'function') rename(elemToRename);
        } else {
            // Native replacement for :contains("call")
            if (exEipElement.textContent.includes("call")) {
                if (typeof rename_func === 'function') rename_func(cid);
            } else {
                alert("Invalid Rename Target: You can only rename local variables (e.g., [rbp-0x4]) or function names in 'call' instructions.");
            }
        }
    }

    if (evt.key === 'p') {
        const pyOff = document.getElementById('pythonOffcanvas');
        if (pyOff) bootstrap.Offcanvas.getOrCreateInstance(pyOff).toggle();
    }
    if (evt.key === 'n') {
        const noteEl = document.getElementById('notesOffcanvas');
        if (noteEl) {
            if (!noteEl.classList.contains('show')) downloadNotes();
            bootstrap.Offcanvas.getOrCreateInstance(noteEl).toggle();
        }
    }
});