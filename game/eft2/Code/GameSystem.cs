using Sandbox.Network;
using System;
using System.Collections.Generic;
using System.Linq;

public sealed class GameSystem : GameObjectSystem<GameSystem>, Component.INetworkListener, ISceneStartup
{
	private const float ArenaHalfLength = 1400.0f;
	private const float ArenaHalfWidth = 760.0f;
	private const float TackleRadius = 54.0f;
	private const float TackleCooldown = 0.45f;
	private const float PairCooldown = 0.18f;

	private readonly List<PlayerMovement> _players = new();
	private readonly Dictionary<Guid, float> _lastTackleByAttacker = new();
	private readonly Dictionary<string, float> _lastPairTackle = new();
	private bool _arenaSpawned;
	private bool _fallbackSpawned;
	private TimeSince _sinceHostInitialize;
	private Vector3 _ballSpawn = Vector3.Up * 28.0f;

	[Sync( SyncFlags.FromHost )] public int RedScore { get; private set; }
	[Sync( SyncFlags.FromHost )] public int BlueScore { get; private set; }
	[Sync( SyncFlags.FromHost )] public string RoundState { get; private set; } = "warmup";

	public IReadOnlyList<PlayerMovement> Players => _players;
	public Ball Ball { get; private set; }
	public TelemetrySink Telemetry => Scene.Get<TelemetrySink>();

	public static bool HasAuthority => !Networking.IsActive || Networking.IsHost;

	public GameSystem( Scene scene ) : base( scene )
	{
		Listen( Stage.PhysicsStep, 20, PhysicsStep, "EFT2 Core Loop" );
	}

	void ISceneStartup.OnHostInitialize()
	{
		_sinceHostInitialize = 0.0f;

		if ( !Networking.IsActive )
		{
			var config = new LobbyConfig
			{
				Privacy = LobbyPrivacy.Private,
				MaxPlayers = 16,
				Name = "EFT2 Core Loop"
			};

			Networking.CreateLobby( config );
		}
	}

	void ISceneStartup.OnClientInitialize()
	{
		EnsureHud();
	}

	void Component.INetworkListener.OnActive( Connection channel )
	{
		if ( !Networking.IsHost )
			return;

		channel.CanSpawnObjects = false;
		EnsureArena( true );
		SpawnPlayerFor( channel );
		RoundState = "playing";
	}

	void Component.INetworkListener.OnDisconnected( Connection channel )
	{
		if ( !Networking.IsHost )
			return;

		foreach ( var player in _players.Where( p => p.IsValid() && p.Network.OwnerId == channel.Id ).ToArray() )
		{
			if ( Ball?.Carrier == player )
				Ball.ForceLoose( "carrier_disconnected" );

			_players.Remove( player );
			player.GameObject.Destroy();
		}
	}

	public void RegisterPlayer( PlayerMovement player )
	{
		if ( player.IsValid() && !_players.Contains( player ) )
			_players.Add( player );
	}

	public void UnregisterPlayer( PlayerMovement player )
	{
		_players.Remove( player );
	}

	public void RegisterBall( Ball ball )
	{
		if ( ball.IsValid() )
			Ball = ball;
	}

	public void ScoreGoal( PlayerMovement carrier, GoalTrigger goal )
	{
		if ( !HasAuthority || carrier is null )
			return;

		// EFT2 LINKS:
		// Mechanics: M-190
		// Concepts: C-004, C-011
		// Scenarios: S-001, S-005
		if ( carrier.Team == TeamId.Red )
			RedScore++;
		else if ( carrier.Team == TeamId.Blue )
			BlueScore++;

		RoundState = "score_reset";
		Telemetry.Emit( "GoalScored", "E-007", $"team={carrier.Team} player={carrier.DisplayName} red={RedScore} blue={BlueScore}" );
		ResetAfterScore();
		RoundState = "playing";
	}

	public void ResetBall( string reason )
	{
		if ( !HasAuthority )
			return;

		Ball?.ResetTo( _ballSpawn, reason );
	}

	public void RespawnPlayer( PlayerMovement player )
	{
		if ( !HasAuthority || !player.IsValid() )
			return;

		player.RespawnAt( FindSpawnTransform( player.Team ) );
	}

	private void PhysicsStep()
	{
		if ( !HasAuthority )
			return;

		EnsureHostFallback();
		_players.RemoveAll( p => !p.IsValid() );
		ResolveTackles();
		CheckOutOfBounds();
	}

	private void EnsureHostFallback()
	{
		if ( Networking.IsActive )
			return;

		if ( _fallbackSpawned || _sinceHostInitialize < 1.0f )
			return;

		EnsureArena( false );
		SpawnStandalonePlayer();
		RoundState = "local_test";
		_fallbackSpawned = true;
	}

	private void EnsureArena( bool networked )
	{
		if ( _arenaSpawned )
			return;

		EnsureHud();
		CreateArenaRoot( networked );
		CreateBall( networked );
		_arenaSpawned = true;
	}

	private void EnsureHud()
	{
		if ( Scene.Camera is null )
			return;

		Scene.Camera.GetOrAddComponent<Hud>();
	}

	private void CreateArenaRoot( bool networked )
	{
		var root = NewObject( "EFT2 Core Loop Arena", Vector3.Zero );

		CreateBox( root, "Field", Vector3.Zero, new Vector3( ArenaHalfLength * 2.0f, ArenaHalfWidth * 2.0f, 24.0f ), new Color( 0.11f, 0.28f, 0.12f, 1.0f ), false );
		CreateBox( root, "Center Stripe", Vector3.Up * 14.0f, new Vector3( 36.0f, ArenaHalfWidth * 2.0f, 8.0f ), Color.White.WithAlpha( 0.8f ), false );

		CreateBox( root, "North Wall", new Vector3( 0.0f, ArenaHalfWidth + 32.0f, 74.0f ), new Vector3( ArenaHalfLength * 2.0f + 160.0f, 64.0f, 148.0f ), Color.Gray, false );
		CreateBox( root, "South Wall", new Vector3( 0.0f, -ArenaHalfWidth - 32.0f, 74.0f ), new Vector3( ArenaHalfLength * 2.0f + 160.0f, 64.0f, 148.0f ), Color.Gray, false );
		CreateBox( root, "Red End Wall", new Vector3( -ArenaHalfLength - 32.0f, 0.0f, 74.0f ), new Vector3( 64.0f, ArenaHalfWidth * 2.0f + 64.0f, 148.0f ), new Color( 0.45f, 0.03f, 0.02f, 1.0f ), false );
		CreateBox( root, "Blue End Wall", new Vector3( ArenaHalfLength + 32.0f, 0.0f, 74.0f ), new Vector3( 64.0f, ArenaHalfWidth * 2.0f + 64.0f, 148.0f ), new Color( 0.02f, 0.08f, 0.42f, 1.0f ), false );

		CreateSpawn( root, TeamId.Red, 0, new Vector3( -820.0f, -160.0f, 34.0f ) );
		CreateSpawn( root, TeamId.Red, 1, new Vector3( -820.0f, 160.0f, 34.0f ) );
		CreateSpawn( root, TeamId.Blue, 0, new Vector3( 820.0f, -160.0f, 34.0f ) );
		CreateSpawn( root, TeamId.Blue, 1, new Vector3( 820.0f, 160.0f, 34.0f ) );

		CreateGoal( root, TeamId.Red, new Vector3( ArenaHalfLength - 90.0f, 0.0f, 76.0f ), new Color( 1.0f, 0.02f, 0.02f, 0.55f ) );
		CreateGoal( root, TeamId.Blue, new Vector3( -ArenaHalfLength + 90.0f, 0.0f, 76.0f ), new Color( 0.05f, 0.22f, 1.0f, 0.55f ) );
		CreateResetTrigger( root );

		if ( networked )
			root.NetworkSpawn( null );
	}

	private void CreateBall( bool networked )
	{
		var ballObject = NewObject( "Ball", _ballSpawn );
		ballObject.Tags.Add( "ball" );
		ballObject.WorldScale = 0.55f;

		var renderer = ballObject.AddComponent<ModelRenderer>();
		renderer.Model = Model.Load( "models/dev/box.vmdl" );
		renderer.Tint = new Color( 1.0f, 0.94f, 0.25f, 1.0f );

		var collider = ballObject.AddComponent<SphereCollider>();
		collider.Radius = 28.0f;

		var body = ballObject.AddComponent<Rigidbody>();
		body.Gravity = true;
		body.LinearDamping = 0.01f;
		body.AngularDamping = 0.25f;
		body.MassOverride = 25.0f;

		ballObject.AddComponent<Ball>();

		if ( networked )
			ballObject.NetworkSpawn( null );
	}

	private void CreateSpawn( GameObject parent, TeamId team, int index, Vector3 position )
	{
		var color = team == TeamId.Red ? new Color( 0.8f, 0.04f, 0.03f, 1.0f ) : new Color( 0.04f, 0.18f, 0.95f, 1.0f );
		var pad = CreateBox( parent, $"{team} Spawn {index}", position - Vector3.Up * 20.0f, new Vector3( 170.0f, 120.0f, 14.0f ), color, true );
		var spawn = pad.AddComponent<SpawnPoint>();
		spawn.Team = team;
		spawn.Index = index;
	}

	private void CreateGoal( GameObject parent, TeamId scoringTeam, Vector3 position, Color color )
	{
		var goal = CreateBox( parent, $"{scoringTeam} Goal Trigger", position, new Vector3( 150.0f, 620.0f, 150.0f ), color, true );
		var collider = goal.Components.Get<BoxCollider>();
		collider.IsTrigger = true;
		goal.AddComponent<GoalTrigger>().ScoringTeam = scoringTeam;
	}

	private void CreateResetTrigger( GameObject parent )
	{
		var reset = NewObject( "Ball Reset Trigger", new Vector3( 0.0f, 0.0f, -260.0f ), parent );
		var box = reset.AddComponent<BoxCollider>();
		box.Scale = new Vector3( ArenaHalfLength * 2.8f, ArenaHalfWidth * 2.8f, 120.0f );
		box.IsTrigger = true;
		reset.AddComponent<BallResetTrigger>();
	}

	private GameObject CreateBox( GameObject parent, string name, Vector3 position, Vector3 size, Color tint, bool visualOnly )
	{
		var box = NewObject( name, position, parent );
		box.WorldScale = size / 50.0f;

		var renderer = box.AddComponent<ModelRenderer>();
		renderer.Model = Model.Load( "models/dev/box.vmdl" );
		renderer.Tint = tint;

		var collider = box.AddComponent<BoxCollider>();
		collider.Scale = 50.0f;

		if ( visualOnly )
			collider.IsTrigger = true;

		return box;
	}

	private void SpawnPlayerFor( Connection connection )
	{
		if ( Scene.GetAllComponents<PlayerMovement>().Any( p => p.IsValid() && p.Network.OwnerId == connection.Id ) )
			return;

		var team = ChooseNextTeam();
		var player = CreatePlayerObject( team, connection.DisplayName, FindSpawnTransform( team ) );
		player.GameObject.Network.SetOwnerTransfer( OwnerTransfer.Fixed );
		player.GameObject.NetworkSpawn( connection );
	}

	private void SpawnStandalonePlayer()
	{
		if ( _players.Any( p => p.IsValid() ) )
			return;

		CreatePlayerObject( TeamId.Red, "Local Tester", FindSpawnTransform( TeamId.Red ) );
	}

	private PlayerMovement CreatePlayerObject( TeamId team, string displayName, Transform spawn )
	{
		var playerObject = NewObject( $"{team} Player - {displayName}", spawn.Position );
		playerObject.WorldRotation = spawn.Rotation;
		playerObject.Tags.Add( "player" );

		var controller = playerObject.AddComponent<PlayerController>();
		controller.UseInputControls = false;
		controller.UseCameraControls = false;
		controller.UseLookControls = false;
		controller.UseAnimatorControls = true;
		controller.WalkSpeed = PlayerMovement.BaseMaxSpeed;
		controller.RunSpeed = PlayerMovement.BaseMaxSpeed;
		controller.JumpSpeed = PlayerMovement.JumpVerticalSpeed;
		controller.BrakePower = 0.35f;
		controller.AirFriction = 0.02f;
		controller.ThirdPerson = true;
		controller.CreateBodyRenderer();

		var movement = playerObject.AddComponent<PlayerMovement>();
		movement.Configure( team, displayName );
		RegisterPlayer( movement );

		return movement;
	}

	private TeamId ChooseNextTeam()
	{
		var red = _players.Count( p => p.IsValid() && p.Team == TeamId.Red );
		var blue = _players.Count( p => p.IsValid() && p.Team == TeamId.Blue );
		return red <= blue ? TeamId.Red : TeamId.Blue;
	}

	private Transform FindSpawnTransform( TeamId team )
	{
		var spawns = Scene.GetAllComponents<SpawnPoint>().Where( s => s.Team == team ).ToArray();
		if ( spawns.Length == 0 )
			return new Transform( team == TeamId.Red ? new Vector3( -800.0f, 0.0f, 48.0f ) : new Vector3( 800.0f, 0.0f, 48.0f ) );

		var spawn = Random.Shared.FromArray( spawns );
		return new Transform( spawn.WorldPosition + Vector3.Up * 54.0f, spawn.WorldRotation );
	}

	private void ResolveTackles()
	{
		// EFT2 LINKS:
		// Mechanics: M-120, M-130, M-150, M-160
		// Principles: P-020, P-060 TODO
		// Concepts: C-001, C-002, C-011
		// Scenarios: S-005, S-015, S-022 future validation
		// TODO: head_on/headon/head.on skill is not implemented in this first tackle pass.
		foreach ( var attacker in _players.ToArray() )
		{
			if ( !attacker.IsValid() || attacker.IsKnockedDown || !attacker.IsCharging )
				continue;

			if ( _lastTackleByAttacker.TryGetValue( attacker.GameObject.Id, out var lastAttack ) && Time.Now - lastAttack < TackleCooldown )
				continue;

			foreach ( var target in _players.ToArray() )
			{
				if ( !target.IsValid() || target == attacker || target.Team == attacker.Team || target.IsKnockedDown )
					continue;

				if ( attacker.WorldPosition.Distance( target.WorldPosition ) > TackleRadius )
					continue;

				var pairKey = $"{attacker.GameObject.Id:N}:{target.GameObject.Id:N}";
				if ( _lastPairTackle.TryGetValue( pairKey, out var lastPair ) && Time.Now - lastPair < PairCooldown )
					continue;

				_lastTackleByAttacker[attacker.GameObject.Id] = Time.Now;
				_lastPairTackle[pairKey] = Time.Now;

				var causedFumble = target.IsCarrier && Ball.IsValid();
				Telemetry.Emit( "TackleResolve", "E-001", $"attacker={attacker.DisplayName} target={target.DisplayName} fumble={causedFumble}" );

				if ( causedFumble )
					Ball.FumbleFrom( target, attacker );

				target.KnockDown( attacker );
				break;
			}
		}
	}

	private void CheckOutOfBounds()
	{
		if ( Ball.IsValid() && Ball.WorldPosition.z < -180.0f )
		{
			ResetBall( "fell_out_of_arena" );
		}

		foreach ( var player in _players.ToArray() )
		{
			if ( player.IsValid() && player.WorldPosition.z < -220.0f )
				RespawnPlayer( player );
		}
	}

	private void ResetAfterScore()
	{
		ResetBall( "goal_scored" );

		foreach ( var player in _players.ToArray() )
		{
			RespawnPlayer( player );
		}
	}

	private GameObject NewObject( string name, Vector3 position, GameObject parent = null )
	{
		var gameObject = parent is null ? new GameObject( true, name ) : new GameObject( parent, true, name );
		gameObject.WorldPosition = position;
		return gameObject;
	}
}
