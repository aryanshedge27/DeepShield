// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  MediaRegistry
 * @notice Stores SHA-256 hashes of media files on-chain as tamper-proof proof of existence.
 */
contract MediaRegistry {

    struct Record {
        bool    exists;
        uint256 timestamp;
        address registrar;
        string  metadata;   // JSON string: filename, verdict, fake_score …
    }

    mapping(bytes32 => Record) private registry;

    event Registered(bytes32 indexed hash, address indexed registrar, uint256 timestamp);

    /// @notice Register a new content hash. Reverts if already registered.
    function register(bytes32 hash, string calldata metadata) external {
        require(!registry[hash].exists, "Hash already registered");
        registry[hash] = Record({
            exists:     true,
            timestamp:  block.timestamp,
            registrar:  msg.sender,
            metadata:   metadata
        });
        emit Registered(hash, msg.sender, block.timestamp);
    }

    /// @notice Verify whether a hash was previously registered.
    function verify(bytes32 hash)
        external
        view
        returns (bool exists, uint256 timestamp, address registrar, string memory metadata)
    {
        Record storage r = registry[hash];
        return (r.exists, r.timestamp, r.registrar, r.metadata);
    }
}