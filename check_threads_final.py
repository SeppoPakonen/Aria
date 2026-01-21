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
        return href && href.startsWith('/@');
    });
    return userLinks.map(a => ({
        user: a.innerText,
        href: a.getAttribute('href'),
        parentClasses: a.parentElement.className,
        grandParentClasses: a.parentElement.parentElement.className,
        containerHTML: a.parentElement.parentElement.parentElement.outerHTML.substring(0, 500)
    })).slice(0, 5);
    """
    res = nav.driver.execute_script(script)
    import json
    print(json.dumps(res, indent=2))
else:
    print("Failed to connect.")
