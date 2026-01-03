use anchor_lang::prelude::*;

declare_id!("idcore1111111111111111111111111111111111");

#[program]
pub mod identity_core {
    use super::*;

    /// Create a new identity account with a DID commitment
    pub fn create_identity(
        ctx: Context<CreateIdentity>,
        owner: Pubkey,
        commitment: [u8; 32],
        metadata_uri: String,
    ) -> Result<()> {
        let identity = &mut ctx.accounts.identity;
        let clock = Clock::get()?;

        require!(metadata_uri.len() <= 200, IdentityError::UriTooLong);

        identity.owner = owner;
        identity.commitment = commitment;
        identity.metadata_uri = metadata_uri;
        identity.created_at = clock.unix_timestamp;
        identity.updated_at = clock.unix_timestamp;
        identity.verification_bits = 0;
        identity.recovery_counter = 0;
        identity.bump = ctx.bumps.identity;

        msg!("Identity created for owner: {}", owner);
        Ok(())
    }

    /// Update the DID commitment (for key rotation)
    pub fn update_commitment(
        ctx: Context<UpdateCommitment>,
        new_commitment: [u8; 32],
    ) -> Result<()> {
        let identity = &mut ctx.accounts.identity;
        let clock = Clock::get()?;

        identity.commitment = new_commitment;
        identity.updated_at = clock.unix_timestamp;

        msg!("Commitment updated for identity: {}", identity.owner);
        Ok(())
    }

    /// Set a verification bit (e.g., KYC verified, document verified)
    pub fn set_verification_bit(
        ctx: Context<SetVerificationBit>,
        bit_index: u8,
    ) -> Result<()> {
        let identity = &mut ctx.accounts.identity;

        require!(bit_index < 32, IdentityError::InvalidBitIndex);

        identity.verification_bits |= 1 << bit_index;

        msg!(
            "Verification bit {} set for identity: {}",
            bit_index,
            identity.owner
        );
        Ok(())
    }

    /// Clear a verification bit
    pub fn clear_verification_bit(
        ctx: Context<ClearVerificationBit>,
        bit_index: u8,
    ) -> Result<()> {
        let identity = &mut ctx.accounts.identity;

        require!(bit_index < 32, IdentityError::InvalidBitIndex);

        identity.verification_bits &= !(1 << bit_index);

        msg!(
            "Verification bit {} cleared for identity: {}",
            bit_index,
            identity.owner
        );
        Ok(())
    }

    /// Recover identity with new owner (after recovery period)
    pub fn recover_identity(
        ctx: Context<RecoverIdentity>,
        new_owner: Pubkey,
    ) -> Result<()> {
        let identity = &mut ctx.accounts.identity;
        let clock = Clock::get()?;

        // Simple recovery: require 30 days since last update
        let recovery_period = 30 * 24 * 60 * 60;
        let elapsed = clock.unix_timestamp - identity.updated_at;

        require!(
            elapsed >= recovery_period,
            IdentityError::RecoveryPeriodNotMet
        );

        identity.owner = new_owner;
        identity.recovery_counter += 1;
        identity.updated_at = clock.unix_timestamp;

        msg!("Identity recovered to new owner: {}", new_owner);
        Ok(())
    }
}

// ============ Account Structs ============

#[derive(Accounts)]
#[instruction(owner: Pubkey)]
pub struct CreateIdentity<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + IdentityAccount::INIT_SPACE,
        seeds = [b"identity", owner.key().as_ref()],
        bump
    )]
    pub identity: Account<'info, IdentityAccount>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateCommitment<'info> {
    #[account(
        mut,
        seeds = [b"identity", identity.owner.as_ref()],
        bump = identity.bump
    )]
    pub identity: Account<'info, IdentityAccount>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct SetVerificationBit<'info> {
    #[account(
        mut,
        seeds = [b"identity", identity.owner.as_ref()],
        bump = identity.bump
    )]
    pub identity: Account<'info, IdentityAccount>,

    pub verifier: Signer<'info>,
}

#[derive(Accounts)]
pub struct ClearVerificationBit<'info> {
    #[account(
        mut,
        seeds = [b"identity", identity.owner.as_ref()],
        bump = identity.bump
    )]
    pub identity: Account<'info, IdentityAccount>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct RecoverIdentity<'info> {
    #[account(
        mut,
        seeds = [b"identity", identity.owner.as_ref()],
        bump = identity.bump
    )]
    pub identity: Account<'info, IdentityAccount>,

    pub authority: Signer<'info>,
}

// ============ State Account ============

#[account]
#[derive(InitSpace)]
pub struct IdentityAccount {
    pub owner: Pubkey,
    pub commitment: [u8; 32],
    pub metadata_uri: String,
    pub created_at: i64,
    pub updated_at: i64,
    pub verification_bits: u32,
    pub recovery_counter: u64,
    pub bump: u8,
}

// ============ Errors ============

#[error_code]
pub enum IdentityError {
    #[msg("Metadata URI is too long (max 200 chars)")]
    UriTooLong,

    #[msg("Invalid bit index (must be 0-31)")]
    InvalidBitIndex,

    #[msg("Recovery period not met (30 days required)")]
    RecoveryPeriodNotMet,
}
