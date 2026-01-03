use anchor_lang::prelude::*;

declare_id!("credvault1111111111111111111111111111");

#[program]
pub mod credential_vault {
    use super::*;

    /// Issue a new verifiable credential
    pub fn issue_credential(
        ctx: Context<IssueCredential>,
        credential_type: String,
        claims_hash: [u8; 32],
        issuer_did: String,
        expiry: Option<i64>,
        metadata_uri: String,
    ) -> Result<()> {
        let credential = &mut ctx.accounts.credential;
        let clock = Clock::get()?;

        require!(
            credential_type.len() <= 50,
            CredentialError::TypeTooLong
        );
        require!(
            issuer_did.len() <= 100,
            CredentialError::DidTooLong
        );
        require!(
            metadata_uri.len() <= 200,
            CredentialError::UriTooLong
        );

        credential.owner = ctx.accounts.owner.key();
        credential.credential_type = credential_type;
        credential.claims_hash = claims_hash;
        credential.issuer_did = issuer_did;
        credential.issued_at = clock.unix_timestamp;
        credential.expiry = expiry;
        credential.metadata_uri = metadata_uri;
        credential.revoked = false;
        credential.revocation_reason = None;
        credential.bump = ctx.bumps.credential;

        msg!(
            "Credential issued: {} for owner: {}",
            credential.credential_type,
            credential.owner
        );
        Ok(())
    }

    /// Revoke a credential
    pub fn revoke_credential(
        ctx: Context<RevokeCredential>,
        reason: String,
    ) -> Result<()> {
        let credential = &mut ctx.accounts.credential;

        require!(
            reason.len() <= 200,
            CredentialError::ReasonTooLong
        );

        credential.revoked = true;
        credential.revocation_reason = Some(reason);

        msg!("Credential revoked for owner: {}", credential.owner);
        Ok(())
    }

    /// Grant access to a credential (selective disclosure)
    pub fn grant_access(
        ctx: Context<GrantAccess>,
        grantee: Pubkey,
        purpose: String,
        expires_at: i64,
        field_mask: u64,
    ) -> Result<()> {
        let access_grant = &mut ctx.accounts.access_grant;
        let clock = Clock::get()?;

        require!(
            purpose.len() <= 200,
            CredentialError::PurposeTooLong
        );
        require!(
            expires_at > clock.unix_timestamp,
            CredentialError::InvalidExpiry
        );

        access_grant.credential = ctx.accounts.credential.key();
        access_grant.grantor = ctx.accounts.owner.key();
        access_grant.grantee = grantee;
        access_grant.purpose = purpose;
        access_grant.expires_at = expires_at;
        access_grant.field_mask = field_mask;
        access_grant.revoked = false;
        access_grant.bump = ctx.bumps.access_grant;

        msg!(
            "Access granted from {} to {} for credential: {}",
            access_grant.grantor,
            grantee,
            access_grant.credential
        );
        Ok(())
    }

    /// Revoke an access grant
    pub fn revoke_access_grant(ctx: Context<RevokeAccessGrant>) -> Result<()> {
        let access_grant = &mut ctx.accounts.access_grant;

        access_grant.revoked = true;

        msg!(
            "Access grant revoked for grantee: {}",
            access_grant.grantee
        );
        Ok(())
    }

    /// Verify a credential (returns verified status)
    pub fn verify_credential(
        ctx: Context<VerifyCredential>,
        expected_hash: [u8; 32],
    ) -> Result<()> {
        let credential = &ctx.accounts.credential;
        let clock = Clock::get()?;

        // Check if credential is not revoked
        require!(!credential.revoked, CredentialError::CredentialRevoked);

        // Check if not expired
        if let Some(expiry) = credential.expiry {
            require!(expiry > clock.unix_timestamp, CredentialError::CredentialExpired);
        }

        // Verify claims hash
        require!(
            credential.claims_hash == expected_hash,
            CredentialError::HashMismatch
        );

        msg!("Credential verified: {}", credential.credential_type);
        Ok(())
    }
}

// ============ Account Structs ============

#[derive(Accounts)]
#[instruction(
    credential_type: String,
    issuer_did: String,
    metadata_uri: String,
)]
pub struct IssueCredential<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + CredentialAccount::INIT_SPACE,
        seeds = [
            b"credential",
            owner.key().as_ref(),
            credential_type.as_bytes(),
            issuer_did.as_bytes()
        ],
        bump
    )]
    pub credential: Account<'info, CredentialAccount>,

    /// Owner of the credential
    pub owner: Signer<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct RevokeCredential<'info> {
    #[account(
        mut,
        seeds = [
            b"credential",
            credential.owner.as_ref(),
            credential.credential_type.as_bytes(),
            credential.issuer_did.as_bytes()
        ],
        bump = credential.bump
    )]
    pub credential: Account<'info, CredentialAccount>,

    pub issuer: Signer<'info>,
}

#[derive(Accounts)]
#[instruction(purpose: String)]
pub struct GrantAccess<'info> {
    #[account(
        seeds = [
            b"credential",
            credential.owner.as_ref(),
            credential.credential_type.as_bytes(),
            credential.issuer_did.as_bytes()
        ],
        bump = credential.bump
    )]
    pub credential: Account<'info, CredentialAccount>,

    /// Owner of the credential granting access
    pub owner: Signer<'info>,

    #[account(
        init,
        payer = payer,
        space = 8 + AccessGrantAccount::INIT_SPACE,
        seeds = [
            b"access",
            credential.key().as_ref(),
            owner.key().as_ref(),
            purpose.as_bytes()
        ],
        bump
    )]
    pub access_grant: Account<'info, AccessGrantAccount>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct RevokeAccessGrant<'info> {
    #[account(
        mut,
        seeds = [
            b"access",
            access_grant.credential.as_ref(),
            access_grant.grantor.as_ref(),
            access_grant.purpose.as_bytes()
        ],
        bump = access_grant.bump
    )]
    pub access_grant: Account<'info, AccessGrantAccount>,

    pub grantor: Signer<'info>,
}

#[derive(Accounts)]
pub struct VerifyCredential<'info> {
    #[account(
        seeds = [
            b"credential",
            credential.owner.as_ref(),
            credential.credential_type.as_bytes(),
            credential.issuer_did.as_bytes()
        ],
        bump = credential.bump
    )]
    pub credential: Account<'info, CredentialAccount>,
}

// ============ State Accounts ============

#[account]
#[derive(InitSpace)]
pub struct CredentialAccount {
    pub owner: Pubkey,
    pub credential_type: String,
    pub claims_hash: [u8; 32],
    pub issuer_did: String,
    pub issued_at: i64,
    pub expiry: Option<i64>,
    pub metadata_uri: String,
    pub revoked: bool,
    pub revocation_reason: Option<String>,
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct AccessGrantAccount {
    pub credential: Pubkey,
    pub grantor: Pubkey,
    pub grantee: Pubkey,
    pub purpose: String,
    pub expires_at: i64,
    pub field_mask: u64,
    pub revoked: bool,
    pub bump: u8,
}

// ============ Errors ============

#[error_code]
pub enum CredentialError {
    #[msg("Credential type is too long (max 50 chars)")]
    TypeTooLong,

    #[msg("Issuer DID is too long (max 100 chars)")]
    DidTooLong,

    #[msg("Metadata URI is too long (max 200 chars)")]
    UriTooLong,

    #[msg("Revocation reason is too long (max 200 chars)")]
    ReasonTooLong,

    #[msg("Purpose is too long (max 200 chars)")]
    PurposeTooLong,

    #[msg("Invalid expiry time")]
    InvalidExpiry,

    #[msg("Credential is revoked")]
    CredentialRevoked,

    #[msg("Credential is expired")]
    CredentialExpired,

    #[msg("Claims hash mismatch")]
    HashMismatch,
}
