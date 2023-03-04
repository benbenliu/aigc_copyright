const { task } = require("hardhat/config");
const { getContract, getAccount } = require("./helpers");
//const { ethers, upgrades } = require('hardhat');
const ContractName = 'DavinciMind';


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

