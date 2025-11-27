// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Inventory {
    struct Item {
        string rfid;
        string name;
        uint256 lastUpdated;
    }

    mapping(string => Item) public items;
    event ItemUpdated(string rfid, string name, uint256 timestamp);

    function updateItem(string memory _rfid, string memory _name) public {
        items[_rfid] = Item(_rfid, _name, block.timestamp);
        emit ItemUpdated(_rfid, _name, block.timestamp);
    }

    function getItem(string memory _rfid) public view returns (string memory, string memory, uint256) {
        Item memory item = items[_rfid];
        return (item.rfid, item.name, item.lastUpdated);
    }
}
