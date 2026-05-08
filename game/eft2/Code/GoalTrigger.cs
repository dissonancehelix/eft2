public sealed class GoalTrigger : Component, Component.ITriggerListener
{
	[Property] public TeamId ScoringTeam { get; set; } = TeamId.none;

	void Component.ITriggerListener.OnTriggerEnter( Collider other )
	{
		if ( !GameSystem.HasAuthority )
			return;

		var player = other.GameObject.Components.Get<PlayerMovement>( FindMode.InAncestors );
		if ( !player.IsValid() || !player.IsCarrier || player.Team != ScoringTeam )
			return;

		// EFT2 LINKS:
		// Mechanics: M-190
		// Concepts: C-004, C-011
		// Scenarios: S-001
		GameSystem.Current?.ScoreGoal( player, this );
	}
}
