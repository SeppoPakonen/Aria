from navigator import AriaNavigator
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "src"))

nav = AriaNavigator()
if nav.connect_to_session(browser_name="firefox"):
    script = """
    const links = Array.from(document.querySelectorAll('a'));
    const userLinks = links.filter(a => {
        const href = a.getAttribute('href');
        return href && href.startsWith('/@') && !href.includes('/post/');
    });
    return userLinks.map(a => {
        let p = a.parentElement;
        let classes = [];
        while(p && p !== document.body) {
            classes.push(p.tagName + "." + p.className);
            p = p.parentElement;
        }
        return {
            user: a.innerText,
            path: classes.slice(0, 5)
        };
    }).slice(0, 5);
    """
    res = nav.driver.execute_script(script)
    import json
    print(json.dumps(res, indent=2))
else:
    print("Failed to connect.")
