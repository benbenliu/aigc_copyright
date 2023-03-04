document.addEventListener("DOMContentLoaded", function() {

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const docForm = document.getElementById("doc-form");
const walletAddressInput = document.getElementById("wallet-address");

connectWalletBtn.addEventListener("click", async () => {
  try {
    // Connect to Metamask
    const provider = await detectEthereumProvider();
    if (provider) {
      await provider.request({ method: "eth_requestAccounts" });
      console.log("Connected to wallet:", provider.selectedAddress);
      walletAddressInput.value = provider.selectedAddress;
    } else {
      console.log("Please install Metamask to connect your wallet");
    }
  } catch (error) {
    console.error(error);
  }
});

docForm.addEventListener("submit", (event) => {
  // Prevent the form from submitting before wallet address is obtained
  if (!walletAddressInput.value) {
    event.preventDefault();
    console.log("Please connect your wallet before submitting the form");
  }
});

});

