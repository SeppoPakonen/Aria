from navigator import AriaNavigator
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "src"))

nav = AriaNavigator()
if nav.connect_to_session(browser_name="firefox"):
    script = """
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while(node = walk.nextNode()){
        if(node.textContent.includes("svuorikoski")) {
            let p = node.parentElement;
            let path = [];
            while(p && p !== document.body) {
                path.push({
                    tag: p.tagName,
                    class: p.className,
                    label: p.getAttribute('aria-label'),
                    role: p.getAttribute('role'),
                    href: p.getAttribute('href')
                });
                p = p.parentElement;
            }
            return path;
        }
    }
    return "NOT_FOUND";
    """
    res = nav.driver.execute_script(script)
    import json
    print(json.dumps(res, indent=2))
else:
    print("Failed to connect.")
