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
        if(node.textContent.includes("samiperttila")) {
            let p = node.parentElement;
            while(p) {
                if (p.tagName === 'DIV' && p.className.length > 0) {
                    return {
                        tag: p.tagName,
                        class: p.className,
                        html: p.outerHTML.substring(0, 500)
                    };
                }
                p = p.parentElement;
            }
        }
    }
    return "NOT_FOUND";
    """
    res = nav.driver.execute_script(script)
    import json
    print(json.dumps(res, indent=2))
else:
    print("Failed to connect.")
