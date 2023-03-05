const { task } = require("hardhat/config");
const { getContract, getAccount, getEnvVariable } = require("./helpers");
const ContractName = 'DavinciMind';
const fs = require('fs');
const path = require('path');


//npx hardhat deploy
task("deploy", "Deploys the rns contract").setAction(async function (taskArguments, hre) {
		const nftContractFactory = await ethers.getContractFactory(ContractName);
		const nft = await hre.upgrades.deployProxy(nftContractFactory);
		await nft.deployed();
		console.log(`${nft.address}`);
});

// npx hardhat verify (合约地址) --network mainnet

task("total_supply", "get supply of nft")
 .setAction(async function (taskArguments, hre) {
 	const contract = await getContract(ContractName, hre);
 	const transactionResponse = await contract.totalSupply();
 	console.log(`total supply is: ${transactionResponse}`);
 });


task("get_abi", "get contract abi")
.setAction(async function (taskArguments, hre) {
 	const artifactsPath = path.join(__dirname, '..', `artifacts/contracts/${ContractName}.sol`);
    const abiFilePath = path.join(artifactsPath, `${ContractName}.json`);

    const abiJson = fs.readFileSync(abiFilePath, 'utf8');
    console.log(abiJson);
 });

task("airdrop1", "airdrop1")
.setAction(async function (taskArguments, hre) {
	const contract = await getContract(ContractName, hre);
	//空投地址待定
	const transactionResponse = await contract.mintAigcNft("de2f2cb9-276e-4158-b6c6-244a394b057c",
	"0xF36060D054d6088Ce669094683771dDAC2e09789", "VtpPU8YgEh92m61Yy39HA42rZjUFGHQ7oW7MFn7PL3M=",
	'{"lib": "cryptography.fernet", "version": "39.0.2"}', {
		gasLimit: 500_000,
	});
	console.log(`Transaction Hash: ${transactionResponse.hash}`);
});
