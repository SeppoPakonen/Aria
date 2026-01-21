from navigator import AriaNavigator
import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), "src"))

nav = AriaNavigator()
if nav.connect_to_session(browser_name="firefox"):
    # Click Slumber Party
    script_click = """
    const el = Array.from(document.querySelectorAll('a[data-list-item-id^="private-channels-"]'))
        .find(a => {
            const label = a.getAttribute('aria-label');
            return label && label.includes('Slumber Party');
        });
    if (el) {
        const events = ['mousedown', 'mouseup', 'click'];
        events.forEach(type => {
            const ev = new MouseEvent(type, { view: window, bubbles: true, cancelable: true });
            el.dispatchEvent(ev);
        });
        return "CLICKED";
    }
    return "NOT_FOUND";
    """
    print(f"Click DM: {nav.driver.execute_script(script_click)}")
    time.sleep(5)
    
    # Dump messages from main
    script_msgs = """
    const main = document.querySelector('main') || document.querySelector('div[class*="chatContent"]');
    if (!main) return "MAIN_NOT_FOUND";
    return Array.from(main.querySelectorAll('li[id^="chat-messages-"]')).map(li => li.innerText).slice(-5);
    """
    msgs = nav.driver.execute_script(script_msgs)
    print(f"Messages: {msgs}")
else:
    print("Failed to connect.")
