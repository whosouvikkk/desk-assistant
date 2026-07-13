// When the user clicks the extension toolbar icon, open the persistent side panel
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});
