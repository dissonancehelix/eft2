public sealed class BallResetTrigger : Component, Component.ITriggerListener
{
	void Component.ITriggerListener.OnTriggerEnter( Collider other )
	{
		if ( !GameSystem.HasAuthority )
			return;

		var ball = other.GameObject.Components.Get<Ball>( FindMode.InAncestors );
		if ( ball.IsValid() )
		{
			// EFT2 LINKS:
			// Mechanics: M-160
			// Concepts: C-011
			GameSystem.Current?.ResetBall( "fall_trigger" );
			return;
		}

		var player = other.GameObject.Components.Get<PlayerMovement>( FindMode.InAncestors );
		if ( player.IsValid() )
		{
			GameSystem.Current?.RespawnPlayer( player );
		}
	}
}
