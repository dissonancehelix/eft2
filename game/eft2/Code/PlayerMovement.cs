using System;

public sealed class PlayerMovement : Component
{
	public const float BaseMaxSpeed = 350.0f;
	public const float CarrierSpeed = 262.5f;
	public const float ChargeThreshold = 300.0f;
	public const float ZeroToChargeSeconds = 1.0f;
	public const float ZeroToMaxSeconds = 1.5f;
	public const float JumpVerticalSpeed = 200.0f;
	public const float KnockdownDuration = 2.75f;

	private const float RecoveryGraceSeconds = 0.15f;

	[RequireComponent] public PlayerController Controller { get; set; }

	[Sync( SyncFlags.FromHost )] public TeamId Team { get; private set; } = TeamId.None;
	[Sync( SyncFlags.FromHost )] public bool IsCarrier { get; private set; }
	[Sync( SyncFlags.FromHost )] public bool IsKnockedDown { get; private set; }
	[Sync( SyncFlags.FromHost )] public float KnockdownRemaining { get; private set; }
	[Sync] public bool IsCharging { get; private set; }
	[Sync] public float ChargeSpeed { get; private set; }

	public string DisplayName { get; private set; } = "Player";
	public bool CanPickup => !IsKnockedDown && _pickupGrace <= 0.0f;
	public Vector3 FlatVelocity => Controller.Velocity.WithZ( 0 );

	private SkinnedModelRenderer _bodyRenderer;
	private float _currentMoveSpeed;
	private float _pickupGrace;
	private bool _registered;

	protected override void OnAwake()
	{
		Controller.UseInputControls = false;
		Controller.UseCameraControls = false;
		Controller.UseLookControls = false;
		Controller.UseAnimatorControls = true;
		Controller.WalkSpeed = BaseMaxSpeed;
		Controller.RunSpeed = BaseMaxSpeed;
		Controller.JumpSpeed = JumpVerticalSpeed;
		Controller.ThirdPerson = true;
		Controller.BrakePower = 0.35f;
		Controller.AirFriction = 0.02f;

		if ( !Controller.Renderer.IsValid() )
		{
			Controller.CreateBodyRenderer();
		}

		_bodyRenderer = Controller.Renderer;
	}

	protected override void OnStart()
	{
		Register();
	}

	protected override void OnDestroy()
	{
		GameSystem.Current?.UnregisterPlayer( this );
	}

	protected override void OnFixedUpdate()
	{
		UpdateKnockdownClock();
		UpdateMovement();
		UpdateCamera();
		UpdateVisuals();
	}

	public void Configure( TeamId team, string displayName )
	{
		if ( GameSystem.HasAuthority )
		{
			Team = team;
			DisplayName = string.IsNullOrWhiteSpace( displayName ) ? $"{team} Player" : displayName;
		}

		UpdateVisuals();
		Register();
	}

	public void SetCarrier( bool isCarrier )
	{
		if ( !GameSystem.HasAuthority )
			return;

		IsCarrier = isCarrier;
		_pickupGrace = isCarrier ? 0.0f : 0.2f;
	}

	public void KnockDown( PlayerMovement attacker )
	{
		if ( !GameSystem.HasAuthority || IsKnockedDown )
			return;

		// EFT2 LINKS:
		// Mechanics: M-120, M-130
		// Principles: P-020, P-060 TODO
		// Concepts: C-001, C-011
		// Scenarios: S-015
		IsKnockedDown = true;
		KnockdownRemaining = KnockdownDuration;
		Controller.WishVelocity = Vector3.Zero;

		var shove = (WorldPosition - attacker.WorldPosition).WithZ( 0 );
		if ( shove.LengthSquared > 0.01f )
		{
			Controller.Body.Velocity = shove.Normal * 160.0f + Vector3.Up * 60.0f;
		}

		GameSystem.Current?.Telemetry.Emit( "PlayerKnockdown", "E-005", $"player={DisplayName} attacker={attacker.DisplayName}" );
	}

	public void RespawnAt( Transform transform )
	{
		if ( !GameSystem.HasAuthority )
			return;

		WorldTransform = transform;
		Controller.Body.Velocity = Vector3.Zero;
		Controller.WishVelocity = Vector3.Zero;
		IsKnockedDown = false;
		KnockdownRemaining = 0.0f;
		_pickupGrace = RecoveryGraceSeconds;
	}

	private void Register()
	{
		if ( _registered )
			return;

		GameSystem.Current?.RegisterPlayer( this );
		_registered = true;
	}

	private void UpdateMovement()
	{
		// EFT2 LINKS:
		// Mechanics: M-110, M-150
		// Principles: P-020, P-050
		// Concepts: C-001, C-002
		if ( _pickupGrace > 0.0f )
		{
			_pickupGrace = MathF.Max( 0.0f, _pickupGrace - Time.Delta );
		}

		if ( IsProxy )
			return;

		if ( IsKnockedDown )
		{
			Controller.WishVelocity = Vector3.Zero;
			IsCharging = false;
			ChargeSpeed = 0.0f;
			return;
		}

		var input = Input.AnalogMove;
		var targetSpeed = IsCarrier ? CarrierSpeed : BaseMaxSpeed;
		var accel = BaseMaxSpeed / ZeroToMaxSeconds;

		_currentMoveSpeed = MoveTowards( _currentMoveSpeed, input.LengthSquared > 0.01f ? targetSpeed : 0.0f, accel * Time.Delta );
		Controller.WishVelocity = input.Normal * _currentMoveSpeed;

		if ( Input.Pressed( "Jump" ) && Controller.IsOnGround )
		{
			Controller.Jump( Vector3.Up * JumpVerticalSpeed );
		}

		var flatSpeed = FlatVelocity.Length;
		ChargeSpeed = flatSpeed;
		IsCharging = flatSpeed >= ChargeThreshold;

		if ( Controller.WishVelocity.LengthSquared > 0.01f )
		{
			Controller.EyeAngles = Rotation.Slerp( Controller.EyeAngles, Controller.WishVelocity.EulerAngles, Time.Delta * 8.0f );
		}
	}

	private void UpdateKnockdownClock()
	{
		if ( !GameSystem.HasAuthority || !IsKnockedDown )
			return;

		KnockdownRemaining = MathF.Max( 0.0f, KnockdownRemaining - Time.Delta );
		if ( KnockdownRemaining > 0.0f )
			return;

		IsKnockedDown = false;
		_pickupGrace = RecoveryGraceSeconds;
		GameSystem.Current?.Telemetry.Emit( "PlayerRecovered", "E-006", $"player={DisplayName}" );
	}

	private void UpdateCamera()
	{
		if ( IsProxy || Scene.Camera is null )
			return;

		if ( Networking.IsActive && Network.Owner != Connection.Local )
			return;

		var focus = WorldPosition + Vector3.Up * 48.0f;
		Scene.Camera.WorldPosition = focus + Vector3.Backward * 520.0f + Vector3.Up * 620.0f;
		Scene.Camera.WorldRotation = Rotation.LookAt( focus - Scene.Camera.WorldPosition, Vector3.Up );
	}

	private void UpdateVisuals()
	{
		if ( !_bodyRenderer.IsValid() )
			_bodyRenderer = Controller.Renderer;

		if ( !_bodyRenderer.IsValid() )
			return;

		var tint = Team switch
		{
			TeamId.Red => new Color( 1.0f, 0.12f, 0.08f, 1.0f ),
			TeamId.Blue => new Color( 0.1f, 0.35f, 1.0f, 1.0f ),
			_ => Color.White
		};

		if ( IsCarrier )
			tint = tint.LerpTo( Color.White, 0.3f );

		if ( IsKnockedDown )
			tint = tint.Desaturate( 0.65f );

		_bodyRenderer.Tint = tint;
	}

	private static float MoveTowards( float current, float target, float maxDelta )
	{
		if ( MathF.Abs( target - current ) <= maxDelta )
			return target;

		return current + MathF.Sign( target - current ) * maxDelta;
	}
}
