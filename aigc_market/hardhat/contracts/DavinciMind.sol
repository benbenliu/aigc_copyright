// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import "@openzeppelin/contracts-upgradeable/token/ERC721/ERC721Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/IERC721EnumerableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/IERC721MetadataUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/ERC721EnumerableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/extensions/ERC721BurnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/IERC721Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC721/IERC721ReceiverUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/introspection/ERC165Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/introspection/IERC165Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";


contract DavinciMind is ERC721Upgradeable, ERC721EnumerableUpgradeable, ERC721BurnableUpgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeMathUpgradeable for uint256;

    mapping(uint256 => bytes32) private tokenIdToEncryptionKey;
    // tokenId to encryptor spec
    mapping(uint256 => string) private tokenIdToEncryptor;
    mapping(uint256 => string) public tokenIdToDocId;

    event AigcMinted(string _docId, address indexed _wallet, uint256 _tokenId);
    event AigcBurned(string _docId, address indexed _wallet, uint256 _tokenId);

    string private baseURI;
    address private destination;

    // do any admin operations but receive fund
    bytes32 public constant SECONDARY_ADMIN_ROLE = keccak256("SECONDARY_ADMIN_ROLE");
    mapping(address => bool) private isBlockedAddress;

    function initialize() initializer public {
        __ERC721_init("Davinci Mind", "AIGC");

        // todo: change to our pindata
        baseURI = "https://dev-api-1.rns.id/api/v2/portal/identity/nft/";
        __AccessControl_init();
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SECONDARY_ADMIN_ROLE, msg.sender);
        // set contract deployer to be admin role of default and secondary admin role
        _setRoleAdmin(DEFAULT_ADMIN_ROLE, DEFAULT_ADMIN_ROLE);
        _setRoleAdmin(SECONDARY_ADMIN_ROLE, DEFAULT_ADMIN_ROLE);
        destination = msg.sender;
    }

    function setBaseURI(string memory _URI) external onlyRole(SECONDARY_ADMIN_ROLE) {
        baseURI = _URI;
    }

    function setIsBlockedAddress(address _wallet, bool _isBlocked) external onlyRole(SECONDARY_ADMIN_ROLE) {
        isBlockedAddress[_wallet] = _isBlocked;
    }

    function getEncryptionKey(uint256 _tokenId) external view returns (bytes32) {
        _requireMinted(_tokenId);
        require(msg.sender == ownerOf(_tokenId));
        return tokenIdToEncryptionKey[_tokenId];
    }

    function getEncryptor(uint256 _tokenId) external view returns (string memory) {
        _requireMinted(_tokenId);
        require(msg.sender == ownerOf(_tokenId));
        return tokenIdToEncryptor[_tokenId];
    }

    function getDocId(uint256 _tokenId) external view returns (string memory) {
        _requireMinted(_tokenId);
        return tokenIdToDocId[_tokenId];
    }

    function setEncryptionKey(uint256 _tokenId, bytes32 _encryptionKey) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _requireMinted(_tokenId);
        tokenIdToEncryptionKey[_tokenId] = _encryptionKey;
    }

    function setEncryptor(uint256 _tokenId, string memory _encryptor) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _requireMinted(_tokenId);
        tokenIdToEncryptor[_tokenId] = _encryptor;
    }

    function setDocId(uint256 _tokenId, string memory _docId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _requireMinted(_tokenId);
        tokenIdToDocId[_tokenId] = _docId;
    }

    function mintAigcNft(string memory _docId, address _wallet, bytes32 _encryptionKey, string memory _encryptor) external onlyRole(SECONDARY_ADMIN_ROLE) nonReentrant {
        require(!isBlockedAddress[_wallet], "the wallet is blacklisted");
        uint256 tokenId = totalSupply().add(1);
        _safeMint(_wallet, tokenId);
        tokenIdToEncryptionKey[tokenId] = _encryptionKey;
        tokenIdToEncryptor[tokenId] = _encryptor;
        tokenIdToDocId[tokenId] = _docId;
        emit AigcMinted(_docId, _wallet, tokenId);
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return baseURI;
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        _requireMinted(tokenId);
        return bytes(baseURI).length > 0 ? string(abi.encodePacked(baseURI, tokenIdToDocId[tokenId],'.json')) : "";
    }

    function setFundDestination(address _destination) public onlyRole(DEFAULT_ADMIN_ROLE) {
        destination = _destination;
    }

    function withdraw() public onlyRole(DEFAULT_ADMIN_ROLE) {
        payable(destination).transfer(address(this).balance);
    }

    function supportsInterface(bytes4 _interfaceId) public view override (ERC721Upgradeable, ERC721EnumerableUpgradeable, AccessControlUpgradeable) returns (bool) {
        return super.supportsInterface(_interfaceId);
    }

    function burn(uint256 _tokenId) public override(ERC721BurnableUpgradeable) {
        super.burn(_tokenId);
        emit AigcBurned(tokenIdToDocId[_tokenId], ownerOf(_tokenId), _tokenId);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721Upgradeable, ERC721EnumerableUpgradeable) {
        if (from != address(0)) {
            address owner = ownerOf(tokenId);
            require(owner == msg.sender, "Only the owner of NFT can transfer or burn it");
            require(to == address(0) || from == address(0), "an RnsID NFT can only be airdropped or burned");
        }
        super._beforeTokenTransfer(from, to, tokenId, 1);
    }
}