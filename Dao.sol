// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Dao {
    struct Proposal {
        string description;
        uint256 voteCount;
        bool executed;
        address payable recipient;
        uint256 amount;
    }

    address public owner;
    mapping(address => uint256) public tokens;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public votes;
    uint256 public proposalCount;

    event ProposalCreated(uint256 proposalId, string description);
    event Voted(uint256 proposalId, address voter);
    event ProposalExecuted(uint256 proposalId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    modifier hasNotVoted(uint256 proposalId) {
        require(
            !votes[msg.sender][proposalId],
            "Already voted on this proposal"
        );
        _;
    }

    modifier proposalExists(uint256 proposalId) {
        require(proposalId < proposalCount, "Proposal does not exist");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addTokens(address to, uint256 amount) external onlyOwner {
        tokens[to] += amount;
    }

    function createProposal(
        string calldata description,
        address payable recipient,
        uint256 amount
    ) external {
        proposals[proposalCount] = Proposal(
            description,
            0,
            false,
            recipient,
            amount
        );
        emit ProposalCreated(proposalCount, description);
        proposalCount++;
    }

    function vote(
        uint256 proposalId
    ) external hasNotVoted(proposalId) proposalExists(proposalId) {
        require(tokens[msg.sender] > 0, "No tokens to vote");

        proposals[proposalId].voteCount += tokens[msg.sender];
        votes[msg.sender][proposalId] = true;

        emit Voted(proposalId, msg.sender);
    }

    function executeProposal(
        uint256 proposalId
    ) external proposalExists(proposalId) {
        Proposal storage proposal = proposals[proposalId];

        require(!proposal.executed, "Proposal already executed");
        require(
            proposal.voteCount > (address(this).balance / 2),
            "Not enough votes"
        );

        proposal.executed = true;

        // Executing the proposal's action
        proposal.recipient.transfer(proposal.amount);

        emit ProposalExecuted(proposalId);
    }
}
