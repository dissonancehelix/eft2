using System;
using System.Linq;

public sealed class Ball : Component
{
	public const float PickupRadius = 58.0f;
	public const float FumbleHorizontalMultiplier = 1.75f;
	public const float FumbleVerticalPop = 128.0f;
	public const float PreviousCarrierPickupImmunity = 1.0f;

	[RequireComponent] public Rigidbody Body { get; set; }

	[Sync( SyncFlags.FromHost )] public PlayerMovement Carrier { get; private set; }
	[Sync( SyncFlags.FromHost )] public bool IsLoose { get; private set; } = true;

	private ModelRenderer _renderer;
	private PlayerMovement _blockedPickupPlayer;
	private float _blockedPickupUntil;
	private float _globalPickupBlockUntil;
	private Vector3 _spawnPosition;

	protected override void OnAwake()
	{
		_renderer = Components.Get<ModelRenderer>();
		Body.Gravity = true;
		Body.LinearDamping = 0.01f;
		Body.AngularDamping = 0.25f;
		Body.MassOverride = 25.0f;
	}

	protected override void OnStart()
	{
		_spawnPosition = WorldPosition;
		GameSystem.Current?.RegisterBall( this );
	}

	protected override void OnFixedUpdate()
	{
		if ( GameSystem.HasAuthority )
		{
			UpdateCarrierPosition();
			TryAutomaticPickup();
		}

		UpdateVisuals();
	}

	public void ResetTo( Vector3 position, string reason )
	{
		if ( !GameSystem.HasAuthority )
			return;

		// EFT2 LINKS:
		// Mechanics: M-160
		// Concepts: C-011
		ClearCarrier();
		IsLoose = true;
		WorldPosition = position;
		WorldRotation = Rotation.Identity;
		Body.Enabled = true;
		Body.Velocity = Vector3.Zero;
		Body.AngularVelocity = Vector3.Zero;
		_blockedPickupPlayer = null;
		_blockedPickupUntil = 0.0f;
		_globalPickupBlockUntil = Time.Now + 0.25f;

		GameSystem.Current?.Telemetry.Emit( "BallReset", "E-004", $"reason={reason} pos={FormatVec( position )}" );
	}

	public void FumbleFrom( PlayerMovement previousCarrier, PlayerMovement attacker )
	{
		if ( !GameSystem.HasAuthority || previousCarrier is null || Carrier != previousCarrier )
			return;

		// EFT2 LINKS:
		// Mechanics: M-150, M-160
		// Principles: P-020
		// Concepts: C-001, C-002, C-011
		ClearCarrier();
		IsLoose = true;
		GameObject.SetParent( null, true );
		WorldPosition = previousCarrier.WorldPosition + Vector3.Up * 42.0f;
		Body.Enabled = true;

		var sourceVelocity = previousCarrier.FlatVelocity;
		if ( sourceVelocity.LengthSquared < 1.0f && attacker is not null )
		{
			sourceVelocity = attacker.FlatVelocity;
		}

		Body.Velocity = sourceVelocity * FumbleHorizontalMultiplier + Vector3.Up * FumbleVerticalPop;
		Body.AngularVelocity = Vector3.Random * 120.0f;
		_blockedPickupPlayer = previousCarrier;
		_blockedPickupUntil = Time.Now + PreviousCarrierPickupImmunity;
		_globalPickupBlockUntil = 0.0f;

		GameSystem.Current?.Telemetry.Emit( "BallLoose", "E-003", $"from={previousCarrier.DisplayName} attacker={attacker?.DisplayName ?? "unknown"} velocity={FormatVec( Body.Velocity )}" );
	}

	public void ForceLoose( string reason )
	{
		if ( !GameSystem.HasAuthority || IsLoose )
			return;

		var previousCarrier = Carrier;
		ClearCarrier();
		IsLoose = true;
		GameObject.SetParent( null, true );
		WorldPosition = previousCarrier.WorldPosition + Vector3.Up * 42.0f;
		Body.Enabled = true;
		Body.Velocity = previousCarrier.FlatVelocity + Vector3.Up * 80.0f;
		_blockedPickupPlayer = previousCarrier;
		_blockedPickupUntil = Time.Now + PreviousCarrierPickupImmunity;
		_globalPickupBlockUntil = 0.0f;

		GameSystem.Current?.Telemetry.Emit( "BallLoose", "E-003", $"reason={reason} from={previousCarrier.DisplayName}" );
	}

	private void TryAutomaticPickup()
	{
		if ( !IsLoose || Time.Now < _globalPickupBlockUntil )
			return;

		// EFT2 LINKS:
		// Mechanics: M-150
		// Principles: P-020, P-050
		// Concepts: C-001, C-002, C-011
		// Anchor: automatic pickup / autograb is contact-driven, never key-driven.
		var player = GameSystem.Current?.Players
			.Where( p => p.IsValid() && p.CanPickup && CanPickupAfterLegacyImmunity( p ) )
			.OrderBy( p => p.WorldPosition.DistanceSquared( WorldPosition ) )
			.FirstOrDefault( p => p.WorldPosition.Distance( WorldPosition ) <= PickupRadius );

		if ( player is null )
			return;

		Pickup( player );
	}

	private void Pickup( PlayerMovement player )
	{
		IsLoose = false;
		Carrier = player;
		_blockedPickupPlayer = null;
		_blockedPickupUntil = 0.0f;
		_globalPickupBlockUntil = 0.0f;
		player.SetCarrier( true );
		Body.Enabled = false;
		GameObject.SetParent( player.GameObject, true );
		UpdateCarrierPosition();

		GameSystem.Current?.Telemetry.Emit( "PossessionTransfer", "E-002", $"to={player.DisplayName} team={player.Team}" );
	}

	private bool CanPickupAfterLegacyImmunity( PlayerMovement player )
	{
		if ( !_blockedPickupPlayer.IsValid() || Time.Now >= _blockedPickupUntil )
			return true;

		return player != _blockedPickupPlayer;
	}

	private void UpdateCarrierPosition()
	{
		if ( IsLoose || !Carrier.IsValid() )
			return;

		WorldPosition = Carrier.WorldPosition + Vector3.Up * 54.0f + Carrier.WorldRotation.Forward * 18.0f;
		WorldRotation *= Rotation.FromYaw( Time.Delta * 260.0f );
	}

	private void ClearCarrier()
	{
		if ( Carrier.IsValid() )
		{
			Carrier.SetCarrier( false );
		}

		Carrier = null;
	}

	private void UpdateVisuals()
	{
		if ( !_renderer.IsValid() )
			_renderer = Components.Get<ModelRenderer>();

		if ( !_renderer.IsValid() )
			return;

		_renderer.Tint = IsLoose ? new Color( 1.0f, 0.94f, 0.25f, 1.0f ) : Color.White;
		GameObject.WorldScale = IsLoose ? 0.55f : 0.72f;
	}

	private static string FormatVec( Vector3 value )
	{
		return $"{value.x:0.0},{value.y:0.0},{value.z:0.0}";
	}
}
